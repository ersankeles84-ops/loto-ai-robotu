import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(page_title="Loto AI Pro", layout="wide")
st.title("🎰 Loto AI Master - 6+1 Profesyonel Sistem")

tabs = st.tabs(["🔵 Sayısal Loto", "🔴 Süper Loto", "🟢 On Numara", "🟡 Şans Topu"])

def veri_ayikla(metin, tavan):
    # Joker ve tarihleri eleyip sadece kolon sayılarını bulur
    sayilar = []
    satirlar = metin.split('\n')
    for satir in satirlar:
        # 1-90 arası sayıları bul (Tarih ve hafta no elenir)
        bulunanlar = re.findall(r'\b(?:[1-9]|[1-8][0-9]|90)\b', satir)
        # Sadece kolon verisi olabilecek satırları al (6-10 arası sayı içerenler)
        if 6 <= len(bulunanlar) <= 12:
            sayilar.extend([int(s) for s in bulunanlar[:6]]) # Sadece ilk 6 ana sayıyı al
    return sayilar

def oyun_paneli(oyun, adet, tavan, sekme):
    with sekme:
        if f"havuz_{oyun}" not in st.session_state:
            st.session_state[f"havuz_{oyun}"] = ""

        col1, col2 = st.columns(2)
        with col1:
            # Kutuyu boşaltmak için session_state bağlantısı kuruldu
            if f"kutu_{oyun}" not in st.session_state:
                st.session_state[f"kutu_{oyun}"] = ""
                
            giriş = st.text_area("Verileri Buraya Yapıştır", height=150, key=f"text_{oyun}", value=st.session_state[f"kutu_{oyun}"])
            
            if st.button(f"💾 Hafızaya Kaydet ve Kutuyu Temizle", key=f"btn_sv_{oyun}"):
                if giriş:
                    # Veriyi depoya ekle
                    st.session_state[f"havuz_{oyun}"] += "\n" + giriş
                    # Kutuyu boşaltmak için state'i sıfırla
                    st.session_state[f"kutu_{oyun}"] = "" 
                    st.success("✅ Veriler hafızaya eklendi!")
                    st.rerun() # Sayfayı yenileyerek kutuyu boş gösterir

        with col2:
            ayiklanan = veri_ayikla(st.session_state[f"havuz_{oyun}"], tavan)
            st.info(f"📊 Hafızadaki Net Analiz Verisi: {len(ayiklanan)} sayı")
            st.warning("⚠️ 'Hafızayı Sıfırla' butonu tüm geçmişi siler!")
            if st.button(f"🗑️ {oyun} Tüm Hafızasını Sıfırla", key=f"btn_clr_{oyun}"):
                st.session_state[f"havuz_{oyun}"] = ""
                st.rerun()

        if st.button(f"🚀 10 Kolon Tahmini Üret (6+1)", key=f"btn_pre_{oyun}"):
            datalar = veri_ayikla(st.session_state[f"havuz_{oyun}"], tavan)
            if len(datalar) < adet:
                st.error("Hafıza yetersiz! Lütfen geçmiş verileri ekleyin.")
            else:
                st.success("🤖 AI Tahminleri (Ana Sayılar + SüperStar):")
                frekans = pd.Series(datalar).value_counts()
                populer = frekans.index.tolist()
                for i in range(1, 11):
                    ana = sorted(np.random.choice(populer[:20] * 3 + list(range(1, tavan+1)), adet, replace=False))
                    ss = np.random.randint(1, tavan + 1)
                    st.markdown(f"**Kolon {i}:** `{' - '.join(map(str, ana))}` | 🌟 **SüperStar:** `{ss}`")

oyun_paneli("Sayısal Loto", 6, 90, tabs[0])
oyun_paneli("Süper Loto", 6, 60, tabs[1])
oyun_paneli("On Numara", 10, 80, tabs[2])
oyun_paneli("Şans Topu", 5, 34, tabs[3])
