import streamlit as st
import requests, base64, re, random
import numpy as np
from collections import Counter
from datetime import datetime
from itertools import combinations

# --- GITHUB ÇELİK KASA ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_getir(oyun_adi):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return base64.b64decode(r.json()['content']).decode('utf-8')
    except: pass
    return ""

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": "V34 Prime Update", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers=headers).status_code in [200, 201]

# --- PRIME ANALİZ MOTORU ---
class PrimeEngine:
    def __init__(self, raw_data, ayar):
        self.ayar = ayar
        matches = re.findall(r"Sonuç: ([\d\s,]+)", raw_data)
        self.cekilisler = [list(map(int, re.findall(r'\d+', m))) for m in matches]
        
        # Birliktelik ve Frekans
        self.baglar = Counter()
        for c in self.cekilisler:
            for comb in combinations(sorted(c), 2):
                self.baglar[comb] += 1
        self.frekans = Counter([s for c in self.cekilisler for s in c])

    def analiz_et(self, kolon):
        puan = 100.0
        
        # 1. GRUP DAĞILIM FİLTRESİ (Küçük sayı yığılmasını engeller)
        # Sayıları 3 bölgeye ayırıyoruz
        alt_sinir = self.ayar['max'] // 3
        ust_sinir = (self.ayar['max'] // 3) * 2
        grup1 = sum(1 for n in kolon if n <= alt_sinir)
        grup2 = sum(1 for n in kolon if alt_sinir < n <= ust_sinir)
        grup3 = sum(1 for n in kolon if n > ust_sinir)
        
        # Eğer bir grupta 4'ten fazla sayı varsa puanı kır (Yığılma Engeli)
        if grup1 > 3 or grup2 > 3 or grup3 > 3: puan -= 60
        # Her gruptan en az 1 sayı olması idealdir
        if grup1 >= 1 and grup2 >= 1 and grup3 >= 1: puan += 30

        # 2. TEK-ÇİFT VE ARDIŞIKLIK
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if tekler in [0, self.ayar['adet']]: puan -= 50
        if any(kolon[i+1] - kolon[i] == 1 for i in range(len(kolon)-1)): puan -= 15 # Tek ardışık okey, çift ardışık (5-6-7) yasak
        if any(kolon[i+2] - kolon[i] == 2 for i in range(len(kolon)-2)): puan -= 70

        # 3. GEÇMİŞ BİRLİKTELİK PUANI
        for comb in combinations(kolon, 2):
            puan += self.baglar.get(comb, 0) * 4
            
        return puan

# --- ARAYÜZ ---
st.set_page_config(page_title="Loto AI Prime V34", layout="wide")
st.title("🏛️ Loto AI V34: Prime Sovereign")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyunlar.keys()))
ayar = oyunlar[secim]

raw = veri_getir(ayar['dosya'])
engine = PrimeEngine(raw, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 Arşiv")
    st.info(f"Kayıtlı Çekiliş: {len(engine.cekilisler)}")
    with st.form("data_in", clear_on_submit=True):
        t = st.date_input("Tarih", datetime.now())
        s = st.text_input("Sonuçlar")
        if st.form_submit_button("💎 MÜHÜRLE"):
            if s.strip():
                if veri_sakla(ayar['dosya'], raw + f"\nTarih: {t.strftime('%Y-%m-%d')} | Sonuç: {s}"):
                    st.success("Mühürlendi!"); st.rerun()

with col2:
    st.header("🧠 Prime Analiz")
    if st.button("🚀 MASTER ANALİZİ BAŞLAT", use_container_width=True):
        adaylar = []
        for _ in range(200000): # 200 bin deneme
            k = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
            p = engine.analiz_et(k)
            if p > 0: adaylar.append((k, p))
        
        adaylar.sort(key=lambda x: x[1], reverse=True)
        final = []
        for k, p in adaylar:
            if len(final) >= 10: break
            # Benzerlik Savar (Max 1 ortak)
            if not any(len(set(k) & set(f[0])) > 1 for f in final):
                final.append((k, p))

        for i, (k, p) in enumerate(final, 1):
            ekstra = ""
            if secim == "Çılgın Sayısal": ekstra = f" | ⭐ SS: {random.randint(1, 90)}"
            elif secim == "Şans Topu": ekstra = f" | ➕ Artı: {random.randint(1, 14)}"
            st.success(f"**Tahmin {i}:** {' - '.join([f'{x:02d}' for x in k])}{ekstra} (Skor: {p:.1f})")
