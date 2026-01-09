import streamlit as st
import requests, base64, re, random
from collections import Counter
from datetime import datetime
from itertools import combinations

# --- GÜVENLİ VERİ MERKEZİ ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_getir(oyun_adi):
    try:
        url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
        headers = {"Authorization": f"token {TOKEN}"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return base64.b64decode(r.json()['content']).decode('utf-8')
        return ""
    except: return ""

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": "V31 Ultimate Final", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers=headers).status_code in [200, 201]

# --- ANA ANALİZ VE SİSTEM BEYNİ ---
class UltimateBrain:
    def __init__(self, raw_data, ayar):
        self.ayar = ayar
        self.raw = raw_data
        # 1. VERİ KURTARMA: Dosyada ne varsa çek (Tarihli veya Düz)
        self.cekilisler = [list(map(int, re.findall(r'\d+', l))) for l in re.findall(r"Sonuç:.*", raw_data)]
        if not self.cekilisler:
            all_nums = [int(n) for n in re.findall(r'\d+', raw_data) if 0 < int(n) <= ayar['max']]
            self.cekilisler = [all_nums[i:i + ayar['adet']] for i in range(0, len(all_nums), ayar['adet'])]
        
        # 2. BİRLİKTELİK ANALİZİ (Hangi sayılar beraber çıkıyor?)
        self.baglar = Counter()
        for c in self.cekilisler:
            for comb in combinations(sorted(c), 2):
                self.baglar[comb] += 1
        
        self.tum_sayilar = [s for c in self.cekilisler for s in c]
        self.frekans = Counter(self.tum_sayilar)

    def filtrele_ve_puanla(self, kolon):
        puan = 100
        # A) İmkansızlık: Yan yana 3 ardışık sayı (Örn: 5-6-7) elenir
        if any(kolon[i+2] - kolon[i] == 2 for i in range(len(kolon)-2)): return -100
        
        # B) Tek-Çift Dengesi (İdeal: 3-3 veya 4-2)
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if not (2 <= tekler <= self.ayar['adet'] - 2): puan -= 40
        
        # C) Birliktelik Puanı (Geçmişte kanka olan sayılar avantajlıdır)
        for comb in combinations(kolon, 2):
            puan += self.baglar.get(comb, 0) * 3
            
        return puan

# --- ARAYÜZ KATMANI ---
st.set_page_config(page_title="Loto AI Ultimate V31", layout="wide")
st.title("🛡️ Loto AI V31: Ultimate Final")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyunlar.keys()))
ayar = oyunlar[secim]

# Veriyi asla kaybetme, hemen çek!
raw_data = veri_getir(ayar['dosya'])
brain = UltimateBrain(raw_data, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("💾 Veri ve Manuel Kayıt")
    st.metric("Hafızadaki Çekiliş", len(brain.cekilisler))
    
    with st.form("manual_entry", clear_on_submit=True):
        t = st.date_input("Çekiliş Tarihi", datetime.now())
        s = st.text_input("Sonuçları Gir (Virgül/Boşluk)")
        if st.form_submit_button("💎 BULUTA MÜHÜRLE VE TEMİZLE"):
            t_str = t.strftime("%Y-%m-%d")
            if t_str in raw_data: st.error("Bu tarih zaten kayıtlı!")
            elif s.strip():
                yeni = raw_data + f"\nTarih: {t_str} | Sonuç: {s}"
                if veri_sakla(ayar['dosya'], yeni): st.rerun()

with col2:
    st.header("🧠 Merkezi Analiz Çıktısı")
    if st.button("🚀 SİSTEMİ TETİKLE", use_container_width=True):
        with st.status("Veri Bağları ve İmkansızlıklar Analiz Ediliyor..."):
            adaylar = []
            for _ in range(150000):
                k = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
                skor = brain.filtrele_ve_puanla(k)
                if skor > 0: adaylar.append((k, skor))
            
            adaylar.sort(key=lambda x: x[1], reverse=True)
            
            final = []
            for k, s in adaylar:
                if len(final) >= 10: break
                # Sıkı Benzerlik Savar: Max 1 ortak sayı
                if not any(len(set(k) & set(f[0])) > 1 for f in final):
                    final.append((k, s))

        for i, (k, s) in enumerate(final, 1):
            ekstra = ""
            if secim == "Çılgın Sayısal": ekstra = f" | ⭐ SS: {random.randint(1, 90)}"
            elif secim == "Şans Topu": ekstra = f" | ➕ Artı: {random.randint(1, 14)}"
            st.success(f"**Tahmin {i}:** {' - '.join([f'{x:02d}' for x in k])}{ekstra} (Zeka Skoru: {s})")

st.divider()
st.caption("Legacy V31: Hiçbir özellik çıkarılmadı. Veri koruma, tarih analizi ve birliktelik matrisi tam kapasite çalışıyor.")
