import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(page_title="Loto AI Master Pro", layout="wide")
st.title("🎰 Loto AI Master - 6+1 Profesyonel Sistem")

# 4 Oyun Sekmesi
tabs = st.tabs(["🔵 Sayısal Loto", "🔴 Süper Loto", "🟢 On Numara", "🟡 Şans Topu"])

def veri_temizle(metin, tavan):
    # Satır satır oku, tarih ve kısa numaraları (hafta no gibi) ele
    temiz_sayilar = []
    satirlar = metin.split('\n')
    for satir in satirlar:
        # Sadece 1-2 haneli sayıları bul (Tarihleri/Yılları eler)
        adaylar = re.findall(r'\b(?:[1-9]|[1-8][0-9]|90)\b', satir)
        if len(adaylar) >= 6: # Bir loto kolonu en az 6 sayı olmalı
            temiz_sayilar.extend([int(s) for s in adaylar])
    return temiz_sayilar

def analiz_motoru(hafiza, adet, tavan):
    sayilar = veri_temizle(hafiza, tavan)
    if len(sayilar) < adet * 2: return None
    
    frekans = pd.Series(sayilar).value_counts()
    populer = frekans.index.tolist()
    
    tahminler = []
    for _ in range(10):
        # 6 Ana Sayı Seçimi
        havuz = populer[:20] * 5 + list(range(1, tavan + 1))
        ana_kolon = sorted(np.random.choice(havuz, adet, replace=False))
        # 1 SüperStar Seçimi (1-90 arası bağımsız şans)
        super_star = np.random.randint(1, tavan + 1)
        tahminler.append((ana_kolon, super_star))
    return tahminler

def oyun_arayuzu(oyun_adi, adet, tavan, sekme):
    with sekme:
        st.header(f"{oyun_adi} Paneli")
        if f"depo_{oyun_adi}" not in st.session_state:
            st.session_state[f"depo_{oyun_adi}"] = ""

        col1, col2 = st.columns(2)
        with col1:
            giriş = st.text_area(f"Verileri Yapıştır", height=150, key=f"in_{oyun_adi}", help="Tarihli liste yapıştırabilirsiniz, robot ayıklayacaktır.")
            if st.button(f"💾 Hafızaya Kaydet ve Temizle", key=f"sv_{oyun_adi}"):
                if giriş:
                    st.session_state[f"depo_{oyun_adi}"] += "\n" + giriş
                    st.success("✅ Veriler ayıklandı ve hafızaya eklendi!")
                    st.rerun()

        with col2:
            mevcut = st.session_state[f"depo_{oyun_adi}"]
            ayiklanmis = veri_temizle(mevcut, tavan)
            st.info(f"📊 Hafızadaki Net Analiz Verisi: {len(ayiklanmis)} sayı")
            if st.button(f"🗑️ Hafızayı Sıfırla", key=f"clr_{oyun_adi}"):
                st.session_state[f"depo_{oyun_adi}"] = ""
                st.rerun()

        if st.button(f"🚀 10 Kolon Tahmini Üret (6+1)", key=f"pre_{oyun_adi}"):
            tahminler = analiz_motoru(st.session_state[f"depo_{oyun_adi}"], adet, tavan)
            if not tahminler:
                st.error("Hafızada yeterli kolon verisi bulunamadı!")
            else:
                st.success("🤖 AI Tahminleri (Ana Sayılar + SüperStar):")
                for i, (ana, ss) in enumerate(tahminler, 1):
                    st.markdown(f"**Kolon {i}:** `{' - '.join(map(str, ana))}`  |  🌟 **SüperStar:** `{ss}`")

# Oyunları Başlat
oyun_arayuzu("Sayısal Loto", 6, 90, tabs[0])
oyun_arayuzu("Süper Loto", 6, 60, tabs[1])
oyun_arayuzu("On Numara", 10, 80, tabs[2])
oyun_arayuzu("Şans Topu", 5, 34, tabs[3])
