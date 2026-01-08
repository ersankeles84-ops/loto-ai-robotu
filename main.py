import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Loto AI Master Pro", layout="wide")
st.title("🎰 Loto AI Master - Akıllı Hafıza Paneli")

# --- 4 Oyun Sekmesi ---
tab1, tab2, tab3, tab4 = st.tabs(["🔵 Sayısal Loto", "🔴 Süper Loto", "🟢 On Numara", "🟡 Şans Topu"])

def analiz_et(hafiza_verisi, adet, tavan):
    if not hafiza_verisi: return None
    # Karışık metinden sadece sayıları ayıkla
    sayilar = [int(s) for s in hafiza_verisi.replace(',', ' ').split() if s.isdigit() and 1 <= int(s) <= tavan]
    if len(sayilar) < adet: return "Eksik Veri"
    
    frekans = pd.Series(sayilar).value_counts()
    populer = frekans.index.tolist()
    
    tahminler = []
    for _ in range(10):
        # Bilimsel Algoritma: Ağırlıklı Rastgele Seçim
        havuz = populer[:15] * 5 + list(range(1, tavan + 1)) 
        kolon = sorted(np.random.choice(havuz, adet, replace=False))
        tahminler.append(kolon)
    return tahminler

def oyun_paneli(oyun, adet, tavan):
    st.subheader(f"{oyun} Analiz Merkezi")
    
    # Hafıza Değişkenini Başlat
    if f"havuz_{oyun}" not in st.session_state:
        st.session_state[f"havuz_{oyun}"] = ""

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📥 Veri Girişi")
        yeni_veri = st.text_area(f"Eklenecek Sonuçları Buraya Yapıştır (Örn: 2024 veya 2025 yılları)", height=150, key=f"input_{oyun}")
        
        if st.button(f"💾 Hafızaya Ekle ve Temizle", key=f"save_{oyun}"):
            if yeni_veri:
                # Eski hafızanın üzerine yenisini ekle
                st.session_state[f"havuz_{oyun}"] += " " + yeni_veri
                st.success(f"✅ Veriler {oyun} havuzuna başarıyla eklendi!")
                st.rerun() # Kutuyu temizlemek için sayfayı yeniler
            else:
                st.warning("Lütfen önce bir veri yapıştırın!")

    with col2:
        st.markdown("### 🧠 Mevcut Hafıza Durumu")
        mevcut_kapasite = len(st.session_state[f"havuz_{oyun}"].split())
        st.info(f"Hafızadaki toplam veri öğesi: {mevcut_kapasite}")
        
        if st.button(f"🗑️ {oyun} Hafızasını Sıfırla"):
            st.session_state[f"havuz_{oyun}"] = ""
            st.rerun()

    st.divider()
    
    # ANALİZ VE TAHMİN
    col3, col4 = st.columns(2)
    with col3:
        if st.button(f"🚀 {oyun} İçin 10 Kolon Üret"):
            sonuclar = analiz_et(st.session_state[f"havuz_{oyun}"], adet, tavan)
            if sonuclar == "Eksik Veri": 
                st.error("Hafıza boş veya yetersiz! Lütfen önce geçmiş verileri ekleyin.")
            elif sonuclar:
                st.success("🤖 Algoritma En İyi Sonuçları Hesapladı:")
                for i, k in enumerate(sonuclar, 1):
                    st.code(f"Kolon {i}: {' - '.join(map(str, k))}")
    
    with col4:
        st.markdown("#### 🔄 Otomatik Güncelleme")
        if st.button(f"🌐 Resmi Siteden Son Sonucu Çek"):
            st.warning("Bu özellik resmi API bağlantısı gerektirir. Şu an manuel ekleme yapabilirsiniz.")

with tab1: oyun_paneli("Sayısal Loto", 6, 90)
with tab2: oyun_paneli("Süper Loto", 6, 60)
with tab3: oyun_paneli("On Numara", 10, 80)
with tab4: oyun_paneli("Şans Topu", 5, 34)
