import streamlit as st
import requests
import base64
import re
import random

# Bulut Bağlantısı
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json()['sha'] if r.status_code == 200 else None
    content = base64.b64encode(metin.encode()).decode()
    data = {"message": "Hafiza Guncellendi", "content": content}
    if sha: data["sha"] = sha
    requests.put(url, json=data, headers=headers)

def veri_getir(oyun_adi):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    return base64.b64decode(r.json()['content']).decode() if r.status_code == 200 else ""

st.set_page_config(page_title="Loto AI Pro Max", layout="wide")
st.title("🎰 Loto AI Master - Süper Star Destekli")

tab_isimleri = ["Çılgın Sayısal", "Süper Loto", "On Numara", "Şans Topu"]
oyun_ayarlar = {
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6, "star": 90},
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6, "star": 0},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 22, "star": 0},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5, "star": 14}
}

tabs = st.tabs(tab_isimleri)

for i, tab in enumerate(tabs):
    isim = tab_isimleri[i]
    ayar = oyun_ayarlar[isim]
    
    with tab:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.header("📥 Veri Girişi")
            if f"h_{ayar['dosya']}" not in st.session_state:
                st.session_state[f"h_{ayar['dosya']}"] = veri_getir(ayar['dosya'])
            
            mevcut_veriler = st.session_state[f"h_{ayar['dosya']}"]
            sayilar = re.findall(r'\d+', mevcut_veriler)
            st.metric("🧠 Kayıtlı Sayı Adedi", len(sayilar))
            
            # Veri girince silinmesi için key kullanıyoruz
            yeni_giris = st.text_area("Verileri Yapıştır", height=150, key=f"input_{ayar['dosya']}")
            
            if st.button(f"💾 {isim} KAYDET VE TEMİZLE", use_container_width=True):
                if yeni_giris:
                    st.session_state[f"h_{ayar['dosya']}"] += "\n" + yeni_giris
                    veri_sakla(ayar['dosya'], st.session_state[f"h_{ayar['dosya']}"])
                    st.success("Buluta İşlendi! Ekran Temizleniyor...")
                    # Session state'i temizleyip sayfayı yenileyerek kutuyu boşaltıyoruz
                    st.session_state[f"input_{ayar['dosya']}"] = ""
                    st.rerun()

        with col2:
            st.header("🔮 10 Kolon + Süper Star")
            if st.button(f"🚀 {isim} TAHMİN ÜRET", use_container_width=True):
                if len(sayilar) < 10:
                    st.error("Tahmin için biraz veri girmelisin kanka!")
                else:
                    for k in range(1, 11):
                        # Ana Sayılar
                        tahmin = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
                        tahmin_str = " - ".join([f"{n:02d}" for n in tahmin])
                        
                        # Süper Star / Artı Sayı Bölümü
                        if ayar['star'] > 0:
                            star_no = random.randint(1, ayar['star'])
                            st.markdown(f"**Kolon {k}:** `{tahmin_str}` | 🔥 **Star: {star_no:02d}**")
                        else:
                            st.markdown(f"**Kolon {k}:** `{tahmin_str}`")
                    st.balloons()
