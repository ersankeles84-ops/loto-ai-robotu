import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(page_title="Loto AI Master Pro", layout="wide")
st.title("🎰 Loto AI Master - 6+1 Profesyonel Sistem")

# 4 Oyun Sekmesi
tabs = st.tabs(["🔵 Sayısal Loto", "🔴 Süper Loto", "🟢 On Numara", "🟡 Şans Topu"])

def veri_ayikla(metin, tavan):
    sayilar = []
    if not metin: return sayilar
    satirlar = metin.split('\n')
    for satir in satirlar:
        bulunanlar = re.findall(r'\b(?:[1-9]|[1-8][0-9]|90)\b', satir)
        if 6 <= len(bulunanlar) <= 15:
            sayilar.extend([int(s) for s in bulunanlar[:6]])
    return sayilar

def oyun_paneli(oyun, adet, tavan, sekme):
    with sekme:
        # Hafıza Alanı
        if f"depo_{oyun}" not in st.session_state:
            st.session_state[f"depo_{oyun}"] = ""
        
        # Kutuyu sıfırlamak için sayaç (Resetleme Anahtarı)
        if f"reset_{oyun}" not in st.session_state:
            st.session_state[f"reset_{oyun}"] = 0

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📥 Yeni Veri Ekle")
            # Her kayıtta anahtar (key) değiştiği için kutu zorla boşalacak
            giriş = st.text_area(f"Verileri Buraya Yapıştır", height=150, 
                                 key=f"input_{oyun}_{st.session_state[f'reset_{oyun}']}")
            
            if st.button(f"💾 Hafızaya Kaydet ve Kutuyu Boşalt", key=f"btn_sv_{oyun}"):
                if giriş:
                    st.session_state[f"depo_{oyun}"] += "\n" + giriş
                    # ANAHTARI DEĞİŞTİR (Bu işlem kutuyu anında siler)
                    st.session_state[f"reset_{oyun}"] += 1
                    st.success("✅ Hafızaya alındı ve kutu resetlendi!")
                    st.rerun()

        with col2:
            st.subheader("📊 Hafıza Durumu")
            ayiklanan = veri_ayikla(st.session_state[f"depo_{oyun}"], tavan)
            st.info(f"Hafızadaki Net Sayı Adedi: {len(ayiklanan)}")
            if st.button(f"🗑️ {oyun} Hafızasını Komple Sil", key=f"btn_clr_{oyun}"):
                st.session_state[f"depo_{oyun}"] = ""
                st.rerun()

        st.divider()
        if st.button(f"🚀 10 Kolon Üret (6+1 Tahmin)", key=f"btn_pre_{oyun}"):
            datalar = veri_ayikla(st.session_state[f"depo_{oyun}"], tavan)
            if len(datalar) < adet:
                st.error("Hafıza yetersiz! Veri eklemelisiniz.")
            else:
                st.success("🤖 AI 6 Sayı + 1 SüperStar Tahmini:")
                frekans = pd.Series(datalar).value_counts()
                populer = frekans.index.tolist()
                for i in range(1, 11):
                    ana = sorted(np.random.choice(populer[:20]*3 + list(range(1, tavan+1)), adet, replace=False))
                    ss = np.random.randint(1, tavan + 1)
                    st.code(f"Kolon {i}: {' - '.join(map(str, ana))} | ⭐ SüperStar: {ss}")

# Panelleri Çalıştır
oyun_paneli("Sayısal Loto", 6, 90, tabs[0])
oyun_paneli("Süper Loto", 6, 60, tabs[1])
oyun_paneli("On Numara", 10, 80, tabs[2])
oyun_paneli("Şans Topu", 5, 34, tabs[3])
