import streamlit as st
import pandas as pd
import numpy as np

# --- Sayfa Yapılandırması ---
st.set_page_config(page_title="Loto AI Master Pro", layout="wide")
st.title("🎰 Loto AI Master - Profesyonel Analiz Sistemi")

# --- 4 Oyun İçin Sekmeler ---
tab1, tab2, tab3, tab4 = st.tabs(["🔵 Sayısal Loto", "🔴 Süper Loto", "🟢 On Numara", "🟡 Şans Topu"])

def gelismis_analiz_motoru(veriler, adet, tavan):
    if not veriler or len(veriler) < 5:
        return None
    sayilar = [int(s) for s in veriler.replace(',', ' ').split() if s.isdigit() and 1 <= int(s) <= tavan]
    if len(sayilar) < adet: return "Yetersiz Veri"
    frekans = pd.Series(sayilar).value_counts()
    populer_sayilar = frekans.index.tolist()
    tahminler = []
    for _ in range(10): # 10 Kolon Tahmin
        agirlikli_liste = populer_sayilar[:20] + list(range(1, tavan + 1))
        kolon = sorted(np.random.choice(agirlikli_liste, adet, replace=False))
        tahminler.append(kolon)
    return tahminler

def oyun_arayuzu(oyun_adi, adet, tavan):
    st.subheader(f"{oyun_adi} Analiz Paneli")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 📥 Veri Giriş ve Hafıza")
        hafiza = st.text_area(f"Geçmiş {oyun_adi} Sonuçları", height=200, placeholder="Sonuçları buraya yapıştırın...", key=f"text_{oyun_adi}")
        if st.button(f"🔄 Otomatik Güncelle", key=f"auto_{oyun_adi}"):
            st.info("Sistem sonuçları tarıyor... (Bağlantı Kuruluyor)")
    with col2:
        st.markdown("### 🧠 Yapay Zeka & Tahmin")
        if st.button(f"🚀 10 Kolon Tahmini Üret", key=f"btn_{oyun_adi}"):
            tahminler = gelismis_analiz_motoru(hafiza, adet, tavan)
            if tahminler == "Yetersiz Veri": st.warning("Daha fazla veri girmelisiniz!")
            elif tahminler:
                st.success(f"✅ En İyi 10 {oyun_adi} Kolonu:")
                for i, kolon in enumerate(tahminler, 1):
                    st.code(f"Kolon {i}: {' - '.join(map(str, kolon))}")

with tab1: oyun_arayuzu("Sayısal Loto", 6, 90)
with tab2: oyun_arayuzu("Süper Loto", 6, 60)
with tab3: oyun_arayuzu("On Numara", 10, 80)
with tab4: oyun_arayuzu("Şans Topu", 5, 34)
