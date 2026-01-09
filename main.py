import streamlit as st
import requests
import base64
import re
import random
import numpy as np
from collections import Counter
from datetime import datetime

# --- GITHUB VE GÜVENLİK ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    content_encoded = base64.b64encode(metin.encode('utf-8')).decode('utf-8')
    data = {"message": "V28 Titan: Anti-Similar Update", "content": content_encoded}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers=headers).status_code in [200, 201]

def veri_getir(oyun_adi):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    return base64.b64decode(r.json()['content']).decode('utf-8') if r.status_code == 200 else ""

# --- TITAN ANALİZ MOTORU ---
class TitanBrain:
    def __init__(self, raw_data, ayar):
        self.ayar = ayar
        self.raw = raw_data
        # Hafıza Derinliği Kontrolü
        self.sayilar = [int(n) for n in re.findall(r'\d+', raw_data) if 0 < int(n) <= ayar['max']]
        self.frekans = Counter(self.sayilar)
        
    def asal_mi(self, n):
        if n < 2: return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0: return False
        return True

    def monte_carlo_test(self, kolon, iterations=15000):
        target = 3 if self.ayar['adet'] < 10 else 6
        hits = 0
        # Sanal çekilişlerle olasılık testi
        for _ in range(iterations):
            sanal = set(random.sample(range(1, self.ayar['max'] + 1), self.ayar['adet']))
            if len(set(kolon) & sanal) >= target: hits += 1
        return hits / iterations

    def beyin_puanla(self, kolon):
        puan = 100.0
        # 1. Mesafe Filtresi (Ardışık Sayı Kontrolü)
        ardisik = sum(1 for i in range(len(kolon)-1) if kolon[i+1] - kolon[i] == 1)
        if ardisik > 1: puan -= 45
        
        # 2. Tek-Çift Dağılım Analizi
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if tekler == 0 or tekler == self.ayar['adet']: puan -= 35
        
        # 3. Asal Sayı Yoğunluğu
        asallar = sum(1 for n in kolon if self.asal_mi(n))
        if asallar < 1 or asallar > 3: puan -= 20
        
        # 4. Frekans Etkisi (Sıcak Sayılar)
        f_skor = sum(self.frekans.get(n, 0) for n in kolon)
        puan += (f_skor / 10)
        
        return round(puan, 2)

# --- ARAYÜZ ---
st.set_page_config(page_title="Loto AI V28 Titan", layout="wide")
st.title("🛡️ Loto AI V28 Titan-Ultimate")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6, "ekstra": None},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6, "ekstra": "Süper Star"},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10, "ekstra": None},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5, "ekstra": "+1"}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyunlar.keys()))
ayar = oyunlar[secim]

raw_data = veri_getir(ayar['dosya'])
brain = TitanBrain(raw_data, ayar)

c1, c2 = st.columns([1, 2])

with c1:
    st.header("📋 Veri ve Kayıt")
    st.metric("Hafıza Derinliği", f"{len(brain.sayilar)} Sayı")
    
    with st.form("titan_input", clear_on_submit=True):
        tarih = st.date_input("Çekiliş Tarihi", datetime.now())
        girdi = st.text_area("Çekiliş Sonuçlarını Buraya Yapıştır")
        if st.form_submit_button("💎 BULUTA MÜHÜRLE"):
            t_str = tarih.strftime("%Y-%m-%d")
            if t_str in raw_data:
                st.error("Bu tarihli veri zaten mühürlenmiş!")
            elif girdi.strip():
                if veri_sakla(ayar['dosya'], raw_data + f"\nTarih: {t_str} | {girdi}"):
                    st.success("Veri mühürlendi!"); st.rerun()

with c2:
    st.header("🚀 Titan Analiz Çıktısı")
    if st.button("🔥 MASTER ANALİZİ BAŞLAT", use_container_width=True):
        if len(brain.sayilar) < 15:
            st.warning("Hafıza çok zayıf, biraz daha veri gir kanka!")
        else:
            with st.status("Anti-Benzerlik Filtreleri ve Monte Carlo İşleniyor..."):
                havuz = []
                for _ in range(150000): # 150 bin kombinasyon taraması
                    k = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
                    s = brain.beyin_puanla(k)
                    havuz.append((k, s))
                
                havuz.sort(key=lambda x: x[1], reverse=True)
                
                final_10 = []
                for k, s in havuz:
                    if len(final_10) >= 10: break
                    
                    # KRİTİK: BENZERLİK SAVAR (En fazla 2 sayı ortak olabilir)
                    is_similar = False
                    for f_k, f_s, f_m in final_10:
                        if len(set(k) & set(f_k)) > 2: # Baraj: 3 ve üzeri ortaksa elenir
                            is_similar = True
                            break
                    
                    if not is_similar:
                        mc = brain.monte_carlo_test(k)
                        final_10.append((k, s, mc))

            for i, (k, s, mc) in enumerate(final_10, 1):
                ekstra = ""
                if secim == "Çılgın Sayısal": ekstra = f" | ⭐ SS: {random.randint(1, 90)}"
                elif secim == "Şans Topu": ekstra = f" | ➕ Artı: {random.randint(1, 14)}"
                
                txt = ' - '.join([f'{x:02d}' for x in k])
                st.info(f"**Tahmin {i}:** {txt}{ekstra}\n(Güç: %{s} | MC Başarı: {mc:.4f})")

st.divider()
st.sidebar.caption("V28: Anti-Benzerlik Algoritması ve 15.000 Iterasyon Monte Carlo Aktif.")
