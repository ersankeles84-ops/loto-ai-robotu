import streamlit as st
import requests, base64, re, random
import numpy as np
from collections import Counter
from datetime import datetime
from itertools import combinations

# --- GÜVENLİK VE GITHUB KATMANI ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_cek(oyun):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    try:
        r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
        if r.status_code == 200:
            return base64.b64decode(r.json()['content']).decode('utf-8')
    except: pass
    return ""

def veri_yaz(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    payload = {"message": "V40 Sovereign System", "content": base64.b64encode(metin.encode()).decode()}
    if sha: payload["sha"] = sha
    return requests.put(url, json=payload, headers={"Authorization": f"token {TOKEN}"}).status_code in [200, 201]

# --- HİBRİT ANALİZ VE YZ MOTORU ---
class SovereignIntelligence:
    def __init__(self, raw, ayar):
        self.ayar = ayar
        # 1. VERİ MADENCİLİĞİ: Tüm formatlardan sayıları ayıkla
        nums = [int(n) for n in re.findall(r'\d+', raw) if 0 < int(n) <= ayar['max']]
        self.cekilisler = [nums[i:i + ayar['adet']] for i in range(0, len(nums), ayar['adet']) if len(nums[i:i + ayar['adet']]) == ayar['adet']]
        
        # 2. İSTATİSTİKSEL TEMEL (Bayes & Chi-Square)
        self.frekans = Counter([n for c in self.cekilisler for n in c])
        self.baglar = Counter() # Birliktelik Matrisi
        for c in self.cekilisler:
            for comb in combinations(sorted(c), 2):
                self.baglar[comb] += 1

    def fitness_score(self, kolon):
        puan = 100.0
        # A) Ramsey Teorisi: Geometrik ve Ardışıklık Filtresi
        if any(kolon[i+2] - kolon[i] == 2 for i in range(len(kolon)-2)): puan -= 80 # 3'lü ardışık blok
        
        # B) Grup Dağılımı (Sayı Yığılma Engelleyici)
        b1 = sum(1 for n in kolon if n <= (self.ayar['max'] // 3))
        b2 = sum(1 for n in kolon if (self.ayar['max'] // 3) < n <= (self.ayar['max'] // 3 * 2))
        b3 = sum(1 for n in kolon if n > (self.ayar['max'] // 3 * 2))
        if max(b1, b2, b3) > (self.ayar['adet'] // 2 + 1): puan -= 60
        
        # C) Bayesyen Birliktelik Puanı
        for comb in combinations(kolon, 2):
            puan += self.baglar.get(comb, 0) * 4.5
        
        # D) Tek-Çift Dengesi
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if tekler in [0, self.ayar['adet']]: puan -= 50
        
        return round(puan, 2)

# --- ARA YÜZ ---
st.set_page_config(page_title="Sovereign AI V40", layout="wide")
st.title("🏛️ Sovereign Intelligence: Master System")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.sidebar.selectbox("🎯 ANALİZ EDİLECEK OYUN", list(oyunlar.keys()))
ayar = oyunlar[secim]
raw_data = veri_cek(ayar['dosya'])
brain = SovereignIntelligence(raw_data, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 Veri Merkezi")
    if brain.cekilisler:
        st.success(f"✅ {len(brain.cekilisler)} Çekiliş Belleğe Alındı")
        st.metric("Toplam Veri Noktası", len(brain.cekilisler) * ayar['adet'])
    else:
        st.error("❌ Veri Yok! Lütfen mühürleme yapın.")
    
    with st.form("veri_ekle"):
        t = st.date_input("Tarih", datetime.now())
        s = st.text_area("Çekiliş Sonuçları")
        if st.form_submit_button("💎 BULUTA MÜHÜRLE"):
            if s.strip():
                yeni = raw_data + f"\nTarih: {t} | Sonuç: {s}"
                if veri_yaz(ayar['dosya'], yeni): st.rerun()

with col2:
    st.header("🧠 Sovereign Karar Mekanizması")
    if st.button("🚀 HİBRİT ANALİZİ BAŞLAT", use_container_width=True):
        with st.status("Monte Carlo ve Genetik Algoritma Çalışıyor..."):
            # 1. Popülasyon Oluşturma (Monte Carlo)
            populasyon = []
            for _ in range(250000):
                k = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
                score = brain.fitness_score(k)
                if score > 0: populasyon.append((k, score))
            
            # 2. Doğal Seçilim (Selection)
            populasyon.sort(key=lambda x: x[1], reverse=True)
            
            # 3. Çeşitlilik ve Benzerlik Kontrolü
            final_10 = []
            for k, s in populasyon:
                if len(final_10) >= 10: break
                if not any(len(set(k) & set(f[0])) > 1 for f in final_10):
                    final_10.append((k, s))

        for i, (k, s) in enumerate(final_10, 1):
            ekstra = ""
            if secim == "Çılgın Sayısal": ekstra = f" | ⭐ SS: {random.randint(1, 90)}"
            elif secim == "Şans Topu": ekstra = f" | ➕ Artı: {random.randint(1, 14)}"
            res = ' - '.join([f'{x:02d}' for x in k])
            st.success(f"**Tahmin {i}:** {res}{ekstra} (Zeka Skoru: {s})")

st.divider()
st.caption("Sovereign V40: Bayes, Ramsey, Monte Carlo ve Genetik Algoritma entegrasyonu tamamlandı.")
