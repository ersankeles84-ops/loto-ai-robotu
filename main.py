import streamlit as st
import requests, base64, re, random
import numpy as np
from collections import Counter
from itertools import combinations

# --- SİSTEM AYARLARI ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": "V17 Quantum Update", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers={"Authorization": f"token {TOKEN}"}).status_code in [200, 201]

def veri_getir(oyun):
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt", headers={"Authorization": f"token {TOKEN}"})
    return base64.b64decode(r.json()['content']).decode() if r.status_code == 200 else ""

# --- ANALİZ ÇEKİRDEĞİ ---
class QuantumEngine:
    def __init__(self, veriler, oyun_ayar):
        self.sayilar = [int(n) for n in re.findall(r'\d+', veriler)]
        self.ayar = oyun_ayar
        self.frekans = Counter(self.sayilar)
        
    def get_matrix(self): # Co-occurrence (Birliktelik)
        # Basit korelasyon matrisi mantığı
        matrix = {}
        # Son 100 çekilişi bloklar halinde incele
        chunks = [self.sayilar[i:i+self.ayar['adet']] for i in range(0, len(self.sayilar), self.ayar['adet'])]
        for chunk in chunks:
            for pair in combinations(sorted(chunk), 2):
                matrix[pair] = matrix.get(pair, 0) + 1
        return matrix

    def simulate_monte_carlo(self, kolon, iterations=5000):
        hits = 0
        for _ in range(iterations):
            sanal_cekilis = set(random.sample(range(1, self.ayar['max']+1), self.ayar['adet']))
            if len(set(kolon) & sanal_cekilis) >= 3: # 3 ve üzeri tutma oranı
                hits += 1
        return hits / iterations

    def risk_skoru(self, kolon):
        score = 0
        # Popüler desen: 1-31 arası yoğunluk (Doğum tarihleri)
        if sum(1 for n in kolon if n <= 31) >= (self.ayar['adet'] - 1): score += 30
        # Ardışıklık
        if any(kolon[i+1] - kolon[i] == 1 for i in range(len(kolon)-1)): score += 20
        return score

# --- ARAYÜZ ---
st.set_page_config(page_title="Loto AI V17 Quantum-Pro", layout="wide")
st.title("🧪 Loto AI V17 Quantum-Pro")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.sidebar.selectbox("Oyun Modu", list(oyunlar.keys()))
strateji = st.sidebar.radio("Strateji", ["Dengeli", "Agresif (Riskli)", "Minimum Paylaşım"])
ayar = oyunlar[secim]

# Veri Akışı
raw_data = veri_getir(ayar['dosya'])
engine = QuantumEngine(raw_data, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 İstatistik Paneli")
    st.metric("Hafıza Derinliği", f"{len(engine.sayilar)} Sayı")
    st.write("**Hot (Sıcak) Sayılar:**", [f"{k}" for k,v in engine.frekans.most_common(5)])
    
    with st.expander("Veri Yükleme"):
        girdi = st.text_area("Çekilişleri Buraya Aktar")
        if st.button("MÜHÜRLE"):
            if veri_sakla(ayar['dosya'], raw_data + "\n" + girdi): st.rerun()

with col2:
    st.header("🧬 Quantum Analiz Çıktısı")
    if st.button("🚀 SİMÜLASYONU BAŞLAT"):
        with st.status("Monte Carlo ve Korelasyon Matrisi İşleniyor..."):
            matrix = engine.get_matrix()
            final_sets = []
            
            # Simulated Annealing Benzeri Seçim Süreci
            for _ in range(50000):
                if len(final_sets) >= 10: break
                
                kolon = sorted(random.sample(range(1, ayar['max']+1), ayar['adet']))
                
                # Filtreler
                risk = engine.risk_skoru(kolon)
                mc_score = engine.simulate_monte_carlo(kolon)
                
                if strateji == "Minimum Paylaşım" and risk > 10: continue
                if strateji == "Agresif" and mc_score < 0.05: continue
                
                # Çeşitlilik (Aynı kolonu veya çok benzerini üretme)
                if not any(len(set(kolon) & set(f['k'])) > 2 for f in final_sets):
                    final_sets.append({"k": kolon, "risk": risk, "mc": mc_score})

        for i, res in enumerate(final_sets, 1):
            with st.container():
                cols = st.columns([3, 1, 1])
                cols[0].success(f"**Kolon {i}:** {' - '.join([f'{x:02d}' for x in res['k']])}")
                cols[1].caption(f"MC Skoru: {res['mc']:.4f}")
                cols[2].caption(f"Risk: {res['risk']}")
                st.divider()

st.caption("🚨 Dürüstlük Beyanı: Bu sistem matematiksel olasılık ve kapsama motoru kullanır. Kesin kazanç garantisi yoktur.")
