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
    data = {"message": "V33 Sovereign Intelligence", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers=headers).status_code in [200, 201]

# --- BİLİMSEL ANALİZ MOTORU ---
class SovereignIntelligence:
    def __init__(self, raw_data, ayar):
        self.ayar = ayar
        # 1. VERİ TEMİZLEME VE YÜKLEME
        matches = re.findall(r"Sonuç: ([\d\s,]+)", raw_data)
        self.cekilisler = [list(map(int, re.findall(r'\d+', m))) for m in matches]
        
        # Eğer tarihli veri yoksa düz sayıları grupla
        if not self.cekilisler:
            nums = [int(n) for n in re.findall(r'\d+', raw_data) if 0 < int(n) <= ayar['max']]
            self.cekilisler = [nums[i:i+ayar['adet']] for i in range(0, len(nums), ayar['adet'])]

        # 2. BİRLİKTELİK MATRİSİ (Coupling Analysis)
        self.baglar = Counter()
        for c in self.cekilisler:
            for comb in combinations(sorted(c), 2):
                self.baglar[comb] += 1
        
        # 3. FREKANS VE GECİKME (Lag) ANALİZİ
        self.tum_sayilar = [s for c in self.cekilisler for s in c]
        self.frekans = Counter(self.tum_sayilar)

    def analiz_puanla(self, kolon):
        score = 100.0
        
        # A) TOPLAM DEĞER ARALIĞI (Sum Range Theory)
        toplam = sum(kolon)
        min_toplam = (self.ayar['adet'] * (self.ayar['adet'] + 1)) / 2
        max_toplam = self.ayar['adet'] * self.ayar['max'] - min_toplam
        beklenen_ort = (min_toplam + max_toplam) / 2
        if not (beklenen_ort * 0.7 <= toplam <= beklenen_ort * 1.3): score -= 40

        # B) TEK-ÇİFT DENGESİ (Odd-Even Probability)
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if tekler in [0, self.ayar['adet']]: score -= 50 # Hepsi tek veya çift elenir
        elif tekler in [3, self.ayar['adet']//2]: score += 20 # İdeal denge bonusu

        # C) ARDIŞIKLIK VE KAOS (Consecutive/Entropy)
        if any(kolon[i+2] - kolon[i] == 2 for i in range(len(kolon)-2)): score -= 60

        # D) BİRLİKTELİK VE FREKANS (Historical Coupling)
        for comb in combinations(kolon, 2):
            score += self.baglar.get(comb, 0) * 2.5
        
        return score

# --- ARAYÜZ ---
st.set_page_config(page_title="Loto AI Sovereign V33", layout="wide")
st.title("🏛️ Loto AI: Sovereign Intelligence V33")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİMİ", list(oyunlar.keys()))
ayar = oyunlar[secim]

# Veri Akışı
raw_content = veri_getir(ayar['dosya'])
engine = SovereignIntelligence(raw_content, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📂 Veri Arşivi")
    st.info(f"Hafızadaki Kayıt: {len(engine.cekilisler)} Çekiliş")
    
    with st.form("data_form", clear_on_submit=True):
        t_in = st.date_input("Çekiliş Tarihi", datetime.now())
        s_in = st.text_input("Sonuçları Gir")
        if st.form_submit_button("💎 BULUTA MÜHÜRLE"):
            if t_in.strftime("%Y-%m-%d") in raw_content:
                st.error("Bu tarih zaten kayıtlı!")
            elif s_in.strip():
                yeni = raw_content + f"\nTarih: {t_in.strftime('%Y-%m-%d')} | Sonuç: {s_in}"
                if veri_sakla(ayar['dosya'], yeni): st.success("Mühürlendi!"); st.rerun()

with col2:
    st.header("🧠 Sovereign Karar Mekanizması")
    if st.button("🚀 ANALİZİ BAŞLAT", use_container_width=True):
        with st.status("Monte Carlo Simülasyonu ve Olasılık Filtreleri Çalışıyor..."):
            adaylar = []
            for _ in range(150000):
                k = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
                p = engine.analiz_puanla(k)
                if p > 0: adaylar.append((k, p))
            
            adaylar.sort(key=lambda x: x[1], reverse=True)
            
            final_10 = []
            for k, p in adaylar:
                if len(final_10) >= 10: break
                # SIKI BENZERLİK SAVAR (Max 1 ortak sayı)
                if not any(len(set(k) & set(f[0])) > 1 for f in final_10):
                    final_10.append((k, p))

        for i, (k, p) in enumerate(final_10, 1):
            ekstra = ""
            if secim == "Çılgın Sayısal": ekstra = f" | ⭐ SS: {random.randint(1, 90)}"
            elif secim == "Şans Topu": ekstra = f" | ➕ Artı: {random.randint(1, 14)}"
            st.success(f"**Tahmin {i}:** {' - '.join([f'{x:02d}' for x in k])}{ekstra} (Skor: {p:.1f})")

st.divider()
st.caption("V33: Monte Carlo, Birliktelik Matrisi ve Toplam Değer Aralığı filtreleri aktiftir.")
