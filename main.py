import streamlit as st
import requests
import base64
import re
import random

# Bulut Ayarları
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
    if r.status_code == 200:
        return base64.b64decode(r.json()['content']).decode()
    return ""

st.set_page_config(page_title="Loto AI Master", layout="wide")
st.title("🎰 Loto AI Master - Profesyonel Panel")

tab_isimleri = ["Çılgın Sayısal", "Süper Loto", "On Numara", "Şans Topu"]
oyun_ayarlar = {
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6, "ek": "Süper Star", "ek_max": 90},
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6, "ek": None, "ek_max": 0},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 22, "ek": None, "ek_max": 0},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5, "ek": "Artı", "ek_max": 14}
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
            
            mevcut = st.session_state[f"h_{ayar['dosya']}"]
            kayitli_sayilar = re.findall(r'\d+', mevcut)
            st.metric("🧠 Kayıtlı Sayı Adedi", len(kayitli_sayilar))
            
            # Form kullanarak hatayı ve kutu temizleme sorununu kökten çözüyoruz
            with st.form(key=f"form_{ayar['dosya']}", clear_on_submit=True):
                yeni_veri = st.text_area("Verileri Buraya Yapıştır", height=200)
                submit = st.form_submit_button(f"💾 {isim} KAYDET VE TEMİZLE", use_container_width=True)
                
                if submit and yeni_veri:
                    st.session_state[f"h_{ayar['dosya']}"] += "\n" + yeni_veri
                    veri_sakla(ayar['dosya'], st.session_state[f"h_{ayar['dosya']}"])
                    st.success("Buluta Kaydedildi ve Ekran Temizlendi!")
                    st.rerun()

        with col2:
            st.header(f"🔮 10 Kolon Tahmin")
            if st.button(f"🚀 {isim} İÇİN TAHMİN ÜRET", use_container_width=True, key=f"btn_{ayar['dosya']}"):
                if len(kayitli_sayilar) < 10:
                    st.warning("Hafızada yeterli veri yok, rastgele üretiliyor...")
                
                st.write("---")
                for k in range(1, 11):
                    tahmin = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
                    tahmin_str = " - ".join([f"{n:02d}" for n in tahmin])
                    
                    if ayar['ek']:
                        ek_no = random.randint(1, ayar['ek_max'])
                        st.markdown(f"**Kolon {k}:** `{tahmin_str}` | 🔥 **{ayar['ek']}: {ek_no:02d}**")
                    else:
                        st.markdown(f"**Kolon {k}:** `{tahmin_str}`")
                st.write("---")
                st.balloons()
