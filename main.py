import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re

# Sayfa Ayarları
st.set_page_config(page_title="Loto AI Master Pro", layout="wide")
st.title("🎰 Loto AI Master - Tam Otomatik Panel")

# Oyun Ayarları (İsimler Güncellendi)
oyunlar = {
    "Çılgın Sayısal": {"adet": 6, "tavan": 90, "url": "https://lotobil.com/sayisal-loto-sonuclari"},
    "Süper Loto": {"adet": 6, "tavan": 60, "url": "https://lotobil.com/super-loto-sonuclari"},
    "On Numara": {"adet": 10, "tavan": 80, "url": "https://lotobil.com/on-numara-sonuclari"},
    "Şans Topu": {"adet": 5, "tavan": 34, "url": "https://lotobil.com/sans-topu-sonuclari"}
}

def veri_cek_ve_temizle(url, tavan):
    try:
        header = {"User-Agent": "Mozilla/5.0"}
        sayfa = requests.get(url, headers=header, timeout=10)
        soup = BeautifulSoup(sayfa.content, "html.parser")
        metin = soup.get_text()
        # Sadece loto sayılarını (1-tavan arası) ayıkla
        bulunanlar = re.findall(r'\b(?:[1-9]|[1-8][0-9]|90)\b', metin)
        return [int(s) for s in bulunanlar if int(s) <= tavan]
    except:
        return []

tabs = st.tabs(list(oyunlar.keys()))

for i, (ad, ayar) in enumerate(oyunlar.items()):
    with tabs[i]:
        if f"hafiza_{ad}" not in st.session_state: st.session_state[f"hafiza_{ad}"] = []
        
        st.header(f"🔥 {ad} Merkezi")
        
        # OTOMATİK DÜĞME
        if st.button(f"🔄 İnternetten {ad} Sonuçlarını Otomatik Çek", key=f"btn_{ad}"):
            with st.spinner("Güncel sonuçlar taranıyor..."):
                veriler = veri_cek_ve_temizle(ayar["url"], ayar["tavan"])
                if veriler:
                    st.session_state[f"hafiza_{ad}"] = veriler
                    st.success(f"✅ Başarılı! {len(veriler)} adet sayı hafızaya alındı.")
                else:
                    st.error("Veri çekilemedi. Lütfen manuel eklemeyi deneyin.")

        # Durum Göstergesi
        mevcut_veri = st.session_state[f"hafiza_{ad}"]
        st.info(f"🧠 Hafıza Durumu: {len(mevcut_veri)} Sayı")

        # TAHMİN ALANI
        if st.button(f"🚀 {ad} İçin 10 Kolon Analiz Et", key=f"run_{ad}"):
            if len(mevcut_veri) < ayar["adet"]:
                st.error("Hafıza boş! Lütfen önce sonuçları çekin.")
            else:
                st.subheader("🤖 AI Profesyonel Tahminleri")
                frekans = pd.Series(mevcut_veri).value_counts()
                populer = frekans.index.tolist()
                
                for k in range(1, 11):
                    # Zeki Algoritma: Çok çıkanlar ve şanslı sayılar karışımı
                    havuz = populer[:15] * 5 + list(range(1, ayar["tavan"] + 1))
                    kolon = sorted(np.random.choice(havuz, ayar["adet"], replace=False))
                    joker = np.random.randint(1, ayar["tavan"] + 1)
                    st.code(f"Kolon {k}: {' - '.join(map(str, kolon))} | JOKER: {joker}")

        # MANUEL EKLEME (YEDEK PLANI)
        with st.expander("Manuel Veri Girişi / Hafızayı Sıfırla"):
            ek_metin = st.text_area("Kopyaladığın sayıları buraya yapıştır", key=f"area_{ad}")
            if st.button("Hafızaya Ekle", key=f"save_{ad}"):
                yeni_sayilar = [int(s) for s in re.findall(r'\b\d+\b', ek_metin) if int(s) <= ayar["tavan"]]
                st.session_state[f"hafiza_{ad}"].extend(yeni_sayilar)
                st.rerun()
            if st.button("Hafızayı Temizle", key=f"clr_{ad}"):
                st.session_state[f"hafiza_{ad}"] = []
                st.rerun()
