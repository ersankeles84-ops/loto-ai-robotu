import streamlit as st
import requests, base64, re, random
import numpy as np
from collections import Counter

# --- GITHUB BAĞLANTISI ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": f"V21 Titan: {oyun}", "content": base64.b64encode(metin.encode()).decode()}
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

# --- ANALİZ ÇEKİRDEĞİ ---
class TitanEngine:
    def __init__(self, veriler, ayar):
        self.sayilar = [int(n) for n in re.findall(r'\d+', veriler)]
        self.ayar = ayar
        self.frekans = Counter(self.sayilar)

    def monte_carlo_test(self, kolon, iterations=5000):
        target = 3 if self.ayar['adet'] < 10 else 6
        hits = sum(1 for _ in range(iterations) if len(set(kolon) & set(random.sample(range(1, self.ayar['max']+1), self.ayar['adet']))) >= target)
        return hits / iterations

    def filtre_uygula(self, kolon):
        # 1. Mesafe Filtresi: Sayılar arası boşluklar dengeli mi?
        mesafeler = [kolon[i+1] - kolon[i] for i in range(len(kolon)-1)]
        if any(m == 1 for m in mesafeler) and mesafeler.count(1) > 1: return False # Max 1 tane ardışık çift
        
        # 2. Tek-Çift Filtresi: Hepsi tek veya hepsi çift mi?
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if tekler < 1 or tekler == self.ayar['adet']: return False
        
        # 3. Asal Sayı Dengesi: Kolonda mutlaka asal olmalı ama abartılmamalı
        asallar = sum(1 for n in kolon if asal_mi(n))
        if asallar == 0 or asallar > 3: return False
        
        return True

# --- ARAYÜZ ---
st.set_page_config(page_title="Loto AI V21 Titan-Master", layout="wide")
st.title("🛡️ Loto AI V21 Titan-Master")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6, "ekstra": None},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6, "ekstra": "Süper Star"},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10, "ekstra": None},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5, "ekstra": "+1"}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyunlar.keys()))
ayar = oyunlar[secim]

raw_data = veri_getir(ayar['dosya'])
engine = TitanEngine(raw_data, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 Veri Giriş ve Hafıza")
    st.metric(f"{secim} Hafızası", f"{len(engine.sayilar)} Sayı")
    
    with st.form("titan_form", clear_on_submit=True):
        girdi = st.text_area("Yeni Çekilişleri Buraya Aktar", height=200)
        if st.form_submit_button("💎 BULUTA MÜHÜRLE", use_container_width=True):
            if girdi.strip() and veri_sakla(ayar['dosya'], raw_data + "\n" + girdi):
                st.success("Veri mühürlendi ve giriş alanı temizlendi!"); st.rerun()

with col2:
    st.header(f"🧬 {secim} Quantum Tahminleri")
    if st.button("🚀 DERİN ANALİZİ BAŞLAT", use_container_width=True):
        if len(engine.sayilar) < 20:
            st.warning("Analiz için daha fazla geçmiş veriye ihtiyaç var kanka!")
        else:
            with st.status("Algoritmalar ve Monte Carlo Testleri İşleniyor..."):
                final_list = []
                deneme = 0
                while len(final_list) < 10 and deneme < 100000:
                    deneme += 1
                    kolon = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
                    
                    if engine.filtre_uygula(kolon):
                        # Benzerlik Kontrolü (Kolonlar arası çakışma max 2)
                        if not any(len(set(kolon) & set(f['k'])) > 2 for f in final_list):
                            mc_score = engine.monte_carlo_test(kolon)
                            final_list.append({"k": kolon, "mc": mc_score})

            for i, res in enumerate(final_list, 1):
                # Ekstra Kurallar
                ekstra_str = ""
                if secim == "Çılgın Sayısal":
                    ekstra_str = f" | ⭐ SS: {random.randint(1, 90)}"
                elif secim == "Şans Topu":
                    ekstra_str = f" | ➕ Artı: {random.randint(1, 14)}"
                
                txt = ' - '.join([f'{x:02d}' for x in res['k']])
                st.info(f"**Tahmin {i}:** {txt}{ekstra_str} (MC Başarı: {res['mc']:.4f})")

st.divider()
st.sidebar.caption("Titan V21: Monte Carlo + Mesafe + Asal + Tek-Çift Filtreleri Aktif.")
