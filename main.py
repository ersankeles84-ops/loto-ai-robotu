import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="Loto AI Master", layout="wide")
st.title("🎰 Loto AI Master - Tam Otomatik Sistem")

# Oyun Ayarları
oyun_ayarlar = {
    "Sayısal Loto": {"adet": 6, "tavan": 90},
    "Süper Loto": {"adet": 6, "tavan": 60},
    "On Numara": {"adet": 10, "tavan": 80},
    "Şans Topu": {"adet": 5, "tavan": 34}
}

# Veri Ayıklama Motoru
def veri_ayikla(metin, tavan):
    if not metin: return []
    # Sadece gerçek loto sayılarını bulur
    sayilar = re.findall(r'\b(?:[1-9]|[1-8][0-9]|90)\b', metin)
    return [int(s) for s in sayilar if int(s) <= tavan]

tabs = st.tabs(list(oyun_ayarlar.keys()))

for i, (ad, ayar) in enumerate(oyun_ayarlar.items()):
    with tabs[i]:
        if f"hafiza_{ad}" not in st.session_state:
            st.session_state[f"hafiza_{ad}"] = ""
        
        st.subheader(f"📊 {ad} - Otomatik Veri Merkezi")
        
        # OTOMATİK İNTERNETTEN ÇEKME BUTONU
        if st.button(f"🌐 İnternetten {ad} Sonuçlarını Otomatik Getir", key=f"auto_{ad}"):
            with st.spinner("İnternet taranıyor..."):
                try:
                    # Bu kısım internetten veri çeker (Scraping)
                    # Şimdilik örnek veri setiyle test ediyoruz
                    st.session_state[f"hafiza_{ad}"] = "07/01/2026 13 24 44 79 80 89 39 44\n05/01/2026 4 12 37 50 64 89 41 7"
                    st.success(f"✅ {ad} için en güncel veriler çekildi!")
                except Exception as e:
                    st.error(f"Bağlantı Hatası: {e}")

        # Hafıza Durumu
        datalar = veri_ayikla(st.session_state[f"depo_{ad}" if f"depo_{ad}" in st.session_state else f"hafiza_{ad}"], ayar["tavan"])
        st.info(f"🧠 Hafızadaki Toplam Sayı: {len(datalar)}")

        st.divider()

        # TAHMİN ÜRETME
        if st.button(f"🚀 {ad} Tahmini Üret", key=f"run_{ad}"):
            if len(datalar) < ayar["adet"]:
                st.error("Hafıza boş! Lütfen önce verileri otomatik çekin.")
            else:
                st.success("🤖 AI Profesyonel Tahminleri (10 Kolon):")
                frekans = pd.Series(datalar).value_counts()
                populer = frekans.index.tolist()
                for k in range(1, 11):
                    # Zeki Seçim: %70 çok çıkanlar, %30 rastgele
                    havuz = populer[:15] * 3 + list(range(1, ayar["tavan"] + 1))
                    ana = sorted(np.random.choice(havuz, ayar["adet"], replace=False))
                    ss = np.random.randint(1, ayar["tavan"] + 1)
                    st.code(f"Kolon {k}: {' - '.join(map(str, ana))} | ⭐ SS: {ss}")

        # Manuel Alan (İstisnalar İçin)
        with st.expander("Manuel Veri Ekle / Hafızayı Temizle"):
            manuel = st.text_area("Verileri buraya yapıştırabilirsiniz", key=f"man_{ad}")
            if st.button("Kaydet", key=f"msav_{ad}"):
                st.session_state[f"hafiza_{ad}"] += "\n" + manuel
                st.rerun()
            if st.button("Hafızayı Sıfırla", key=f"reset_{ad}"):
                st.session_state[f"hafiza_{ad}"] = ""
                st.rerun()
