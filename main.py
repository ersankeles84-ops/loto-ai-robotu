import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Loto AI Master Pro", layout="wide")
st.title("🎰 Loto AI Master - Tam Otomatik Panel")

# Oyun Ayarları ve Veri Kaynakları
oyunlar = {
    "Çılgın Sayısal": {"adet": 6, "tavan": 90, "url": "https://www.lototurkiye.com/sayisal-loto-sonuclari"},
    "Süper Loto": {"adet": 6, "tavan": 60, "url": "https://www.lototurkiye.com/super-loto-sonuclari"},
    "On Numara": {"adet": 10, "tavan": 80, "url": "https://www.lototurkiye.com/on-numara-sonuclari"},
    "Şans Topu": {"adet": 5, "tavan": 34, "url": "https://www.lototurkiye.com/sans-topu-sonuclari"}
}

def veri_cek_motoru(url, tavan):
    try:
        # Gerçek bir kullanıcı gibi davran (Engel aşmak için)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Sayfadaki tüm metni al ve sayıları cımbızla çek
            ham_metin = soup.get_text()
            temiz_sayilar = re.findall(r'\b(?:[1-9]|[1-8][0-9]|90)\b', ham_metin)
            sayilar = [int(s) for s in temiz_sayilar if int(s) <= tavan]
            # Sadece son 500 sayıyı al (Performans için)
            return sayilar[-500:] if len(sayilar) > 500 else sayilar
        return []
    except:
        return []

tabs = st.tabs(list(oyunlar.keys()))

for i, (ad, ayar) in enumerate(oyunlar.items()):
    with tabs[i]:
        if f"hafiza_{ad}" not in st.session_state: st.session_state[f"hafiza_{ad}"] = []
        
        st.header(f"🔥 {ad} Merkezi")
        
        # OTOMATİK DÜĞME
        if st.button(f"🔄 İnternetten {ad} Sonuçlarını Otomatik Çek", key=f"btn_{ad}"):
            with st.spinner("Sistem interneti tarıyor..."):
                cekilenler = veri_cek_motoru(ayar["url"], ayar["tavan"])
                if len(cekilenler) > 10:
                    st.session_state[f"hafiza_{ad}"] = cekilenler
                    st.success(f"✅ Başarılı! {len(cekilenler)} adet güncel sayı hafızaya alındı.")
                else:
                    st.warning("⚠️ Otomatik çekme şu an kısıtlı. Lütfen aşağıdan manuel veri ekleyin.")

        # Durum
        mevcut = st.session_state[f"hafiza_{ad}"]
        st.info(f"🧠 Hafıza Durumu: {len(mevcut)} Sayı")

        # TAHMİN
        if st.button(f"🚀 {ad} İçin 10 Kolon Analiz Et", key=f"run_{ad}"):
            if len(mevcut) < ayar["adet"]:
                st.error("Hafıza yetersiz! Lütfen veri yükleyin.")
            else:
                st.subheader("🤖 AI Tahminleri (Çok Çıkan Odaklı)")
                seri = pd.Series(mevcut).value_counts()
                populer = seri.index.tolist()
                
                for k in range(1, 11):
                    # Akıllı Havuz: En çok çıkan 20 sayıyı havuzda 5 kat daha fazla bulundurur
                    havuz = populer[:20] * 5 + list(range(1, ayar["tavan"] + 1))
                    kolon = sorted(np.random.choice(havuz, ayar["adet"], replace=False))
                    joker = np.random.randint(1, ayar["tavan"] + 1)
                    st.code(f"Kolon {k}: {' - '.join(map(str, kolon))} | JOKER: {joker}")

        # MANUEL EKLEME
        with st.expander("📝 Manuel Veri Girişi (Eğer internet çekmezse)"):
            metin = st.text_area("Sonuçları buraya yapıştır", key=f"txt_{ad}", help="Tarihleri silmenize gerek yok, robot sadece sayıları alır.")
            if st.button("Hafızaya Ekle", key=f"save_{ad}"):
                yeni = [int(s) for s in re.findall(r'\b\d+\b', metin) if int(s) <= ayar["tavan"]]
                st.session_state[f"hafiza_{ad}"].extend(yeni)
                st.rerun()
