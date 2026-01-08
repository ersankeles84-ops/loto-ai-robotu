import streamlit as st
import requests
import base64
import re
import random
from collections import Counter

# Bulut Bağlantısı
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    sha = r.json()['sha'] if r.status_code == 200 else None
    content_encoded = base64.b64encode(metin.encode('utf-8')).decode('utf-8')
    data = {"message": f"Guncelleme: {oyun_adi}", "content": content_encoded}
    if sha: data["sha"] = sha
    res = requests.put(url, json=data, headers=headers)
    return res.status_code in [200, 201]

def veri_getir(oyun_adi):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return base64.b64decode(r.json()['content']).decode('utf-8')
    return ""

st.set_page_config(page_title="Loto AI Hyper V3", layout="wide")
st.title("🛡️ Loto AI Master - Akıllı Analiz Sistemi")

oyun_ayarlar = {
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6, "ek": "Süper Star", "ek_max": 90},
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6, "ek": None, "ek_max": 0},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 22, "ek": None, "ek_max": 0},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5, "ek": "Artı", "ek_max": 14}
}

tabs = st.tabs(list(oyun_ayarlar.keys()))

for i, tab in enumerate(tabs):
    isim = list(oyun_ayarlar.keys())[i]
    ayar = oyun_ayarlar[isim]
    h_key = f"h_{ayar['dosya']}"
    
    with tab:
        # OTOMATİK HAFIZA YÜKLEME (Uygulama açıldığında verileri çeker)
        if h_key not in st.session_state or st.session_state[h_key] == "":
            with st.spinner(f"{isim} hafızası yükleniyor..."):
                st.session_state[h_key] = veri_getir(ayar['dosya'])

        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.header("📥 Veri Girişi")
            mevcut = st.session_state[h_key]
            tum_sayilar = re.findall(r'\d+', mevcut)
            st.metric("📊 Hafızadaki Sayı", len(tum_sayilar))
            
            # Form kullanarak otomatik temizleme sağlıyoruz
            with st.form(key=f"form_{ayar['dosya']}", clear_on_submit=True):
                yeni_veri = st.text_area("Sonuçları buraya yapıştır", height=150)
                submit = st.form_submit_button("💾 BULUTA KAYDET VE TEMİZLE")
                if submit and yeni_veri:
                    st.session_state[h_key] += "\n" + yeni_veri
                    if veri_sakla(ayar['dosya'], st.session_state[h_key]):
                        st.success("Veriler Buluta Mühürlendi!")
                        st.rerun()

        with col2:
            st.header("🧬 Akıllı Analiz (2 Milyon)")
            if st.button(f"🚀 ANALİZİ BAŞLAT", key=f"anlz_{ayar['dosya']}", use_container_width=True):
                if len(tum_sayilar) < 10:
                    st.warning("Önce veri yükle kanka!")
                else:
                    with st.status("🛸 2 Milyon Kombinasyon Taranıyor...", expanded=True):
                        frekans = Counter(tum_sayilar)
                        adaylar = []
                        # GERÇEK 2 MİLYON TARAMA
                        for _ in range(2000000):
                            kolon = tuple(sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet'])))
                            puan = sum(frekans.get(str(n), 0) for n in kolon)
                            adaylar.append((kolon, puan))
                        
                        # BENZERLİK VE ARDIŞIKLIK FİLTRESİ
                        adaylar.sort(key=lambda x: x[1], reverse=True)
                        en_iyi_on = []
                        for kolon, puan in adaylar:
                            if len(en_iyi_on) >= 10: break
                            # Eğer bu kolon, zaten seçilenlerle %70'den fazla aynıysa geç (Benzerliği engelle)
                            if not any(len(set(kolon) & set(mevcut_k[0])) > (ayar['adet'] * 0.7) for mevcut_k in en_iyi_on):
                                en_iyi_on.append((kolon, puan))

                    st.subheader("📍 Stratejik Farklı 10 Kolon")
                    for k, (kolon, puan) in enumerate(en_iyi_on, 1):
                        k_str = " - ".join([f"{n:02d}" for n in kolon])
                        st.success(f"**Kolon {k}:** {k_str} (Skor: {puan})")
                    st.balloons()
