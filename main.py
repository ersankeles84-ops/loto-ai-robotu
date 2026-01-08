import streamlit as st
import requests
import base64
import re

# Bulut Ayarları (Az önce girdiğin Secrets bilgilerini kullanır)
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json()['sha'] if r.status_code == 200 else None
    content = base64.b64encode(metin.encode()).decode()
    data = {"message": "Hafıza Güncellendi", "content": content}
    if sha: data["sha"] = sha
    requests.put(url, json=data, headers=headers)

def veri_getir(oyun_adi):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    if r.status_code == 200:
        return base64.b64decode(r.json()['content']).decode()
    return ""

st.set_page_config(page_title="Loto AI Bulut", page_icon="🎰")
st.title("🎰 Loto AI - Kalıcı Bulut Hafıza")

# Sekmeleri Oluştur
tab_isimleri = ["Çılgın Sayısal", "Süper Loto", "On Numara", "Şans Topu"]
oyun_dosyalari = ["CilginSayisal", "SuperLoto", "OnNumara", "SansTopu"]
tabs = st.tabs(tab_isimleri)

for i in range(len(tab_isimleri)):
    with tabs[i]:
        oyun = oyun_dosyalari[i]
        isim = tab_isimleri[i]
        
        # Hafızayı GitHub'dan çek
        if f"h_{oyun}" not in st.session_state:
            st.session_state[f"h_{oyun}"] = veri_getir(oyun)
        
        st.subheader(f"🔥 {isim} Merkezi")
        
        # Hafıza Durumu
        sayi_adedi = len(re.findall(r'\d+', st.session_state[f"h_{oyun}"]))
        st.info(f"🧠 Hafıza Durumu: {sayi_adedi} Sayı Kayıtlı")
        
        # Veri Girişi
        yeni_veri = st.text_area(f"{isim} sonuçlarını yapıştır", key=f"input_{oyun}", height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"💾 {isim} KAYDET", key=f"btn_save_{oyun}"):
                if yeni_veri:
                    st.session_state[f"h_{oyun}"] += "\n" + yeni_veri
                    veri_sakla(oyun, st.session_state[f"h_{oyun}"])
                    st.success("GitHub Bulutuna Kaydedildi!")
                    st.rerun()
        with col2:
            if st.button(f"🚀 {isim} ANALİZ ET", key=f"btn_analiz_{oyun}"):
                st.write("Hesaplanıyor...")

