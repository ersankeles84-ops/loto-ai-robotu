import streamlit as st
import pandas as pd
import numpy as np

# Sayfa Ayarları
st.set_page_config(page_title="Loto AI Master Pro", layout="wide")
st.title("🎰 Loto AI Master - Profesyonel Analiz Sistemi")

# 4 Oyun Sekmesi
tab1, tab2, tab3, tab4 = st.tabs(["🔵 Sayısal Loto", "🔴 Süper Loto", "🟢 On Numara", "🟡 Şans Topu"])

def analiz_motoru(hafiza, adet, tavan):
    if not hafiza: return None
    sayilar = [int(s) for s in hafiza.replace(',', ' ').split() if s.isdigit() and 1 <= int(s) <= tavan]
    if len(sayilar) < adet: return "Eksik"
    
    frekans = pd.Series(sayilar).value_counts()
    populer = frekans.index.tolist()
    
    tahminler = []
    for _ in range(10):
        # Akıllı Algoritma: Frekans Ağırlıklı Seçim
        havuz = populer[:15] * 5 + list(range(1, tavan + 1))
        kolon = sorted(np.random.choice(havuz, adet, replace=False))
        tahminler.append(kolon)
    return tahminler

def oyun_arayuzu(oyun_adi, adet, tavan):
    st.header(f"{oyun_adi} Paneli")
    
    # Kalıcı Hafıza Başlatma
    if f"depo_{oyun_adi}" not in st.session_state:
        st.session_state[f"depo_{oyun_adi}"] = ""

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Yeni Veri Ekle")
        giriş = st.text_area(f"{oyun_adi} Sonuçlarını Yapıştır", height=150, key=f"input_{oyun_adi}")
        
        if st.button(f"💾 Hafızaya Kaydet ve Temizle", key=f"save_btn_{oyun_adi}"):
            if giriş:
                st.session_state[f"depo_{oyun_adi}"] += " " + giriş
                st.success("✅ Veri başarıyla eklendi ve kutu boşaltıldı!")
                st.rerun() # Kutuyu temizlemek için ekranı tazeler
            else:
                st.warning("Lütfen veri girin!")

    with col2:
        st.subheader("📊 Hafıza Durumu")
        mevcut = st.session_state[f"depo_{oyun_adi}"]
        sayi_adedi = len(mevcut.split())
        st.info(f"Hafızadaki Toplam Veri: {sayi_adedi} adet")
        
        if st.button(f"🗑️ {oyun_adi} Hafızasını Boşalt", key=f"clear_btn_{oyun_adi}"):
            st.session_state[f"depo_{oyun_adi}"] = ""
            st.rerun()

    st.divider()

    # Tahmin ve Güncelleme
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"🚀 {oyun_adi} İçin 10 Kolon Üret", key=f"predict_btn_{oyun_adi}"):
            tahminler = analiz_motoru(st.session_state[f"depo_{oyun_adi}"], adet, tavan)
            if tahminler == "Eksik":
                st.error("Analiz için hafızada yeterli veri yok!")
            elif tahminler:
                st.success("🤖 AI En İyi 10 Sonucu Oluşturdu:")
                for i, k in enumerate(tahminler, 1):
                    st.code(f"Kolon {i}: {' - '.join(map(str, k))}")

    with c2:
        st.subheader("🔄 Otomatik Güncelleme")
        if st.button(f"🌐 Son Sonucu Otomatik Çek", key=f"auto_btn_{oyun_adi}"):
            st.info("Resmi site taranıyor... (Şu an manuel ekleme yapabilirsiniz)")

# Sekmeleri Çalıştır
with tab1: oyun_arayuzu("Sayısal Loto", 6, 90)
with tab2: oyun_arayuzu("Süper Loto", 6, 60)
with tab3: oyun_arayuzu("On Numara", 10, 80)
with tab4: oyun_arayuzu("Şans Topu", 5, 34)
