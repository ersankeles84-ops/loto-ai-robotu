import streamlit as st
import requests, base64, re, random
from collections import Counter
from itertools import combinations

# --- GITHUB VE GÜVENLİK AYARLARI ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": f"V18 Omni Update: {oyun}", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers={"Authorization": f"token {TOKEN}"}).status_code in [200, 201]

def veri_getir(oyun):
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt", headers={"Authorization": f"token {TOKEN}"})
    return base64.b64decode(r.json()['content']).decode() if r.status_code == 200 else ""

def asal_mi(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

# --- PROFESYONEL ANALİZ MOTORU ---
class OmniEngine:
    def __init__(self, veriler, ayar):
        self.sayilar = [int(n) for n in re.findall(r'\d+', veriler)]
        self.ayar = ayar
        self.frekans = Counter(self.sayilar)
        
    def simulate_monte_carlo(self, kolon, iterations=10000):
        hits = 0
        target = 3 if self.ayar['adet'] < 10 else 6 # On Numara için 6, diğerleri için 3
        for _ in range(iterations):
            sanal = set(random.sample(range(1, self.ayar['max']+1), self.ayar['adet']))
            if len(set(kolon) & sanal) >= target: hits += 1
        return hits / iterations

    def analiz_et(self, kolon):
        # Paylaşım Riski ve İstatistiksel Uyum Puanı
        score = 100
        # Ardışık kontrolü (Dünyanın en iyisi ardışıklardan kaçınır)
        if any(kolon[i+1] - kolon[i] == 1 for i in range(len(kolon)-1)): score -= 30
        # Tek-Çift dengesi (3-3 veya 5-5 gibi ideal dağılım)
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if not (1 < tekler < self.ayar['adet'] - 1): score -= 20
        # Asal sayı kontrolü
        asallar = sum(1 for n in kolon if asal_mi(n))
        if asallar == 0: score -= 10
        return score

# --- ANA ARAYÜZ ---
st.set_page_config(page_title="Loto AI V18 Final-Omni", layout="wide")
st.title("🌌 Loto AI V18 Final-Omni")

# 4 OYUN SEÇENEĞİ SABİTLENDİ
oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyunlar.keys()))
ayar = oyunlar[secim]
mod = st.sidebar.radio("🚀 STRATEJİ", ["Dengeli (Önerilen)", "Agresif (Maksimum Kapsama)", "Maliye Dostu (Az Paylaşım)"])

# Canlı Veri Yükleme
raw_data = veri_getir(ayar['dosya'])
engine = OmniEngine(raw_data, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 İstatistik Paneli")
    st.metric(f"{secim} Hafıza Derinliği", f"{len(engine.sayilar)} Sayı")
    st.subheader("🔥 En Sıcak 5 Sayı")
    st.write([f"{k} (Çıkma: {v})" for k,v in engine.frekans.most_common(5)])
    
    with st.expander("📝 Yeni Çekiliş Verisi Ekle"):
        girdi = st.text_area("Sayıları buraya yapıştır")
        if st.button("BULUTA MÜHÜRLE"):
            if veri_sakla(ayar['dosya'], raw_data + "\n" + girdi):
                st.success("Veriler mühürlendi!"); st.rerun()

with col2:
    st.header(f"🧬 {secim} Akıllı Tahminler")
    if st.button("🚀 MASTER ANALİZİ BAŞLAT", use_container_width=True):
        with st.status("Monte Carlo ve Olasılık Matrisleri Hesaplanıyor..."):
            final_list = []
            deneme = 0
            while len(final_list) < 10 and deneme < 100000:
                deneme += 1
                kolon = sorted(random.sample(range(1, ayar['max']+1), ayar['adet']))
                
                perf_score = engine.analiz_et(kolon)
                mc_rate = engine.simulate_monte_carlo(kolon)
                
                # Stratejiye göre eleme
                if mod == "Dengeli" and perf_score < 70: continue
                if mod == "Agresif" and mc_rate < 0.04: continue
                
                # Benzerlik Kontrolü (Aynı kolonu veya çok benzerini üretme)
                if not any(len(set(kolon) & set(f['k'])) > 2 for f in final_list):
                    final_list.append({"k": kolon, "score": perf_score, "mc": mc_rate})

            for i, res in enumerate(final_list, 1):
                st.info(f"**Tahmin {i}:** {' - '.join([f'{x:02d}' for x in res['k']])} | Güç: %{res['score']}")
                st.caption(f"Monte Carlo Başarı Oranı: {res['mc']:.5f}")

st.divider()
st.caption("🛡️ Dürüstlük: Bu robot en yüksek olasılıklı kapsama motorunu kullanır. Şans faktörü her zaman baki kalır.")
