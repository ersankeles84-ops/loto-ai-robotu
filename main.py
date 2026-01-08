import streamlit as st
import requests
import base64
import re

# Bulut Bağlantısı (Secrets'tan gelen bilgiler)
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
    return base64.b64decode(r.json()['content']).decode() if r.status_code == 200 else ""

st.set_page_config(page_title="Loto AI Bulut", page_icon="🎰")
st.title("🎰 Loto AI - Bulut Hafıza Devrede")

tabs = st.tabs(["Çılgın Sayısal", "Süper Loto", "On Numara", "Şans Topu"])
oyunlar = ["CilginSayisal", "SuperLoto", "OnNumara", "SansTopu"]

for i, tab in enumerate(tabs):
    with tab:
        oyun = oyunlar[i]
        # Hafızayı yükle
        if f"h_{oyun}" not in st.session_state:
            st.session_state[f"h_{oyun}"] = veri_getir(oyun)
        
        st.subheader(f"🔥 {tab.label} Merkezi")
        
        # Hafıza Durumu
        sayi_adedi = len(re.findall(r'\d+', st.session_state[f"h_{oyun}"]))
        st.info(f"🧠 Hafıza Durumu: {sayi_adedi} Sayı Kayıtlı")
        
        # Veri Girişi
        yeni_veri = st.text_area(f"{tab.label} sonuçlarını buraya yapıştır", key=f"input_{oyun}")
        
        if st.button(f"💾 {tab.label} VERİLERİNİ BULUTA ÇAK"):
            if yeni_veri:
                st.session_state[f"h_{oyun}"] += "\n" + yeni_veri
                veri_sakla(oyun, st.session_state[f"h_{oyun}"])
                st.success("Kayıt Başarılı! Veriler GitHub'a kilitlendi.")
                st.rerun()

        if st.button(f"🚀 {tab.label} Analiz Et"):
            st.warning("Analiz algoritması hafızadaki verilere göre hesaplanıyor...")
