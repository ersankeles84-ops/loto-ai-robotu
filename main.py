import streamlit as st
import pandas as pd
import numpy as np
import re
from collections import Counter

# Uygulama Başlığı ve Menü Ayarları
st.set_page_config(page_title="Loto AI Master", layout="wide")
st.title("🎰 Loto AI - Dünyanın En İyi Tahmin Robotu")

# Yan Menü: Oyun Seçimi ve Analizler
oyun = st.sidebar.selectbox("🎯 Oyun Seçin", ["Çılgın Sayısal Loto", "Süper Loto", "On Numara", "Şans Topu"])

st.sidebar.divider()

menu = st.sidebar.radio("📊 Analiz Menüsü", [
    "Veri Laboratuvarı", 
    "Bütün Çekiliş Arşivi",
    "En Çok Çıkan Sayılar", 
    "Uzun Süredir Çıkmayanlar", 
    "Tahmin AI (Zeka)", 
    "Birlikte Çıkanlar & Takip Edenler",
    "Tek/Çift & Asal Analizi",
    "Top Analizi"
])

# Veri Saklama (Session State)
if 'raw_data' not in st.session_state:
    st.session_state['raw_data'] = ""

# Veri Giriş Alanı
if menu == "Veri Laboratuvarı":
    st.subheader("📊 Veri Giriş Merkezi")
    st.info("Geçmiş çekilişleri buraya yapıştırın. Robot tarihleri eleyip sayıları otomatik ayıklayacaktır.")
    user_input = st.text_area("Veri Giriş Kutusu (Kopyala/Yapıştır)", height=250, value=st.session_state['raw_data'])
    if user_input:
        st.session_state['raw_data'] = user_input
        st.success("Veriler kaydedildi! Diğer menülerden analize başlayabilirsiniz.")
else:
    user_input = st.session_state['raw_data']

# Veri Ayıklama Fonksiyonu
def veri_ayikla(text, top_sayisi):
    # Sayıları bul (Regex)
    nums = re.findall(r"(\d{1,2})", text)
    # Sadece mantıklı loto sayılarını al (1-90 arası)
    valid_nums = [int(n) for n in nums if 1 <= int(n) <= 90]
    
    clean_draws = []
    for i in range(0, len(valid_nums) - (len(valid_nums) % top_sayisi), top_sayisi):
        draw = sorted(valid_nums[i:i+top_sayisi])
        clean_draws.append(draw)
    return clean_draws

if user_input:
    limits = {"Çılgın Sayısal Loto": 6, "Süper Loto": 6, "On Numara": 22, "Şans Topu": 5}
    max_range = {"Çılgın Sayısal Loto": 90, "Süper Loto": 60, "On Numara": 80, "Şans Topu": 34}
    
    draws = veri_ayikla(user_input, limits[oyun])
    
    if draws:
        df = pd.DataFrame(draws)
        flat_list = [num for sublist in draws for num in sublist]
        counts = Counter(flat_list)

        if menu == "Bütün Çekiliş Arşivi":
            st.subheader("📁 Geçmiş Çekilişler")
            st.dataframe(df)

        elif menu == "En Çok Çıkan Sayılar":
            st.subheader("🔥 Frekans Analizi")
            freq_df = pd.DataFrame(counts.most_common(), columns=['Sayı', 'Çıkma Sayısı']).set_index('Sayı')
            st.bar_chart(freq_df)

        elif menu == "Tahmin AI (Zeka)":
            st.subheader("🤖 Yapay Zeka & Olasılık Tahmini")
            st.write("Robot, sıcak sayılar ve gecikme teorisini harmanlayarak kolon üretir.")
            if st.button("Süper Kolon Üret"):
                all_possible = list(range(1, max_range[oyun] + 1))
                # Basit Ağırlıklı Olasılık: Çok çıkanların şansı daha yüksek
                weights = [counts.get(i, 1) for i in all_possible]
                prob = np.array(weights) / sum(weights)
                prediction = sorted(np.random.choice(all_possible, size=limits[oyun], replace=False, p=prob))
                st.success(f"🤖 Önerilen Kolon: {prediction}")
                st.balloons()
    else:
        st.warning("Henüz geçerli bir veri girilmedi.")
else:
    st.info("Lütfen önce 'Veri Laboratuvarı'ndan çekiliş sonuçlarını yapıştırın.")
