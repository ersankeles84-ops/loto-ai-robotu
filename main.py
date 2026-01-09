import streamlit as st
import requests
import base64
import re
import random
import numpy as np
from collections import Counter
from datetime import datetime

# --- GITHUB VE GÜVENLİK PROTOKOLÜ ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    content_encoded = base64.b64encode(metin.encode('utf-8')).decode('utf-8')
    data = {"message": f"V27 Grand-Master Update: {oyun_adi}", "content": content_encoded}
    if sha: data["sha"] = sha
    res = requests.put(url, json=data, headers=headers)
    return res.status_code in [200, 201]

def veri_getir(oyun_adi):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return base64.b64decode(r.json()['content']).decode('utf-8')
    return ""

# --- GELİŞMİŞ ANALİZ MOTORU (BEYİN) ---
class GrandMasterBrain:
    def __init__(self, raw_data, ayar):
        self.ayar = ayar
        self.raw = raw_data
        # EVRENSEL VERİ AYIKLAYICI: Hafızadaki her rakamı güvenli sınırlar içinde çeker
        self.sayilar = [int(n) for n in re.findall(r'\d+', raw_data) if 0 < int(n) <= ayar['max']]
        self.frekans = Counter(self.sayilar)
        
    def asal_mi(self, n):
        if n < 2: return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0: return False
        return True

    def monte_carlo_sim(self, kolon, iterations=10000):
        # Üretilen kolonu 10.000 sanal çekilişte test eder
        target = 3 if self.ayar['adet'] < 10 else 6
        hits = 0
        for _ in range(iterations):
            sanal = set(random.sample(range(1, self.ayar['max'] + 1), self.ayar['adet']))
            if len(set(kolon) & sanal) >= target: hits += 1
        return hits / iterations

    def kapsamli_puanla(self, kolon):
        puan = 100
        # 1. Ardışıklık Analizi (Fiziksel İmkansızlık Filtresi)
        ardisik = sum(1 for i in range(len(kolon)-1) if kolon[i+1] - kolon[i] == 1)
        if ardisik > 1: puan -= 40
        
        # 2. Tek-Çift Dengesi (İstatistiki Olasılık)
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if tekler == 0 or tekler == self.ayar['adet']: puan -= 30
        
        # 3. Asal Sayı Dağılımı
        asallar = sum(1 for n in kolon if self.asal_mi(n))
        if asallar < 1 or asallar > 3: puan -= 15
        
        # 4. Frekans Uyumu (Sıcak/Soğuk Dengesi)
        f_skor = sum(self.frekans.get(n, 0) for n in kolon)
        puan += (f_skor / (len(self.sayilar) / self.ayar['adet'] if self.sayilar else 1))
        
        return round(puan, 2)

# --- ANA ARAYÜZ (GÖVDE) ---
st.set_page_config(page_title="Loto AI V27 Grand-Master", layout="wide")
st.title("🏛️ Loto AI V27 Grand-Master")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6, "ekstra": None},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6, "ekstra": "Süper Star (1-90)"},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10, "ekstra": None},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5, "ekstra": "+1 (1-14)"}
}

secim = st.sidebar.selectbox("🎯 ANALİZ EDİLECEK OYUN", list(oyunlar.keys()))
ayar = oyunlar[secim]

# Buluttan Veriyi Çek ve Beyni Çalıştır
raw_data = veri_getir(ayar['dosya'])
brain = GrandMasterBrain(raw_data, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 Arşiv ve Giriş")
    st.metric(f"{secim} Hafızası", f"{len(brain.sayilar)} Sayı")
    
    # Tarihli, Manuel Girişli ve Otomatik Temizlenen Form
    with st.form("grand_master_form", clear_on_submit=True):
        t_tarih = st.date_input("Çekiliş Tarihi", datetime.now())
        s_girdi = st.text_area("Sonuçları Gir (Virgül veya Boşlukla)")
        if st.form_submit_button("💎 BULUTA MÜHÜRLE VE TEMİZLE"):
            t_str = t_tarih.strftime("%Y-%m-%d")
            if t_str in raw_data:
                st.error(f"❌ {t_str} tarihli çekiliş zaten kayıtlı!")
            elif s_girdi.strip():
                yeni_kayit = f"\nTarih: {t_str} | Sonuç: {s_girdi}"
                if veri_sakla(ayar['dosya'], raw_data + yeni_kayit):
                    st.success("✅ Veri mühürlendi, ekran temizlendi!"); st.rerun()

with col2:
    st.header("🧬 Grand-Master Analiz Çıktısı")
    if st.button("🚀 TÜM ALGORİTMALARI ÇALIŞTIR", use_container_width=True):
        if len(brain.sayilar) < 10:
            st.warning("Analiz için önce veri girmelisin kanka!")
        else:
            with st.status("Monte Carlo ve Olasılık Filtreleri Uygulanıyor..."):
                adaylar = []
                for _ in range(100000): # 100.000 Kombinasyon testi
                    kolon = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
                    skor = brain.kapsamli_puanla(kolon)
                    adaylar.append((kolon, skor))
                
                # En yüksek puanlıları seç
                adaylar.sort(key=lambda x: x[1], reverse=True)
                final_10 = []
                for k, s in adaylar:
                    if len(final_10) >= 10: break
                    # Benzerlik Filtresi (Kolonlar arası max 2 sayı)
                    if not any(len(set(k) & set(f[0])) > 2 for f in final_10):
                        mc = brain.monte_carlo_sim(k)
                        final_10.append((k, s, mc))

            for i, (k, s, mc) in enumerate(final_10, 1):
                # Ekstra Kuralları Uygula
                ekstra_txt = ""
                if secim == "Çılgın Sayısal":
                    ekstra_txt = f" | ⭐ SS: {random.randint(1, 90)}"
                elif secim == "Şans Topu":
                    ekstra_txt = f" | ➕ Artı: {random.randint(1, 14)}"
                
                kolon_str = ' - '.join([f'{x:02d}' for x in k])
                st.info(f"**Tahmin {i}:** {kolon_str}{ekstra_txt} \n(Güç Skoru: %{s} | MC Başarı: {mc:.4f})")

st.divider()
st.caption("🚨 V27 Grand-Master: Tam kapasite veri koruma, tarih analizi ve fiziksel imkansızlık filtreleri aktiftir.")
