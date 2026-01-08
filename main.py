import streamlit as st
import requests
import base64
import re
import random
from collections import Counter

# Bulut Bağlantısı - Secrets kısmından çekilir
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    # Önce mevcut dosyanın SHA bilgisini al (Güncelleme için şart)
    r = requests.get(url, headers=headers)
    sha = r.json()['sha'] if r.status_code == 200 else None
    
    content_encoded = base64.b64encode(metin.encode('utf-8')).decode('utf-8')
    data = {"message": f"{oyun_adi} hafiza guncelleme", "content": content_encoded}
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

st.set_page_config(page_title="Loto AI Hyper", layout="wide")
st.title("⚡ Loto AI Hyper - 2 Milyon Kombinasyon Gücü")

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
    h_key = f"h_{ayar['dosya']}"
    
    with tab:
        # OTOMATİK YÜKLEME SİSTEMİ
        if h_key not in st.session_state or st.session_state[h_key] == "":
            with st.spinner(f"{isim} hafızası buluttan çekiliyor..."):
                st.session_state[h_key] = veri_getir(ayar['dosya'])

        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.header("📥 Veri Merkezi")
            mevcut = st.session_state[h_key]
            tum_sayilar = re.findall(r'\d+', mevcut)
            st.metric("📊 Hafızadaki Toplam Sayı", len(tum_sayilar))
            
            # 1. Manuel Giriş (Son Çekiliş)
            with st.expander("🆕 Son Çekiliş Sonucunu Gir", expanded=True):
                with st.form(key=f"tek_{ayar['dosya']}", clear_on_submit=True):
                    son_sonuc = st.text_input("Örn: 09.01.2026 3 12 22 23 45 55")
                    if st.form_submit_button("💾 KAYDET VE TEMİZLE"):
                        st.session_state[h_key] += "\n" + son_sonuc
                        if veri_sakla(ayar['dosya'], st.session_state[h_key]):
                            st.success("Buluta Mühürlendi!")
                            st.rerun()
                        else:
                            st.error("GitHub bağlantı hatası!")

            # 2. Toplu Veri Yükleme
            with st.expander("📚 Toplu Veri Yükle"):
                toplu = st.text_area("Verileri buraya yapıştır", height=150)
                if st.button("💾 BULUTA GÖNDER", key=f"top_{ayar['dosya']}"):
                    st.session_state[h_key] += "\n" + toplu
                    veri_sakla(ayar['dosya'], st.session_state[h_key])
                    st.success("Tüm veriler GitHub'a işlendi!")
                    st.rerun()

        with col2:
            st.header("🧬 2.000.000 Analiz Motoru")
            if st.button(f"🚀 HİPER ANALİZİ BAŞLAT ({isim})", use_container_width=True):
                if len(tum_sayilar) < 10:
                    st.warning("Hafıza boş! Lütfen önce veri yükleyin.")
                else:
                    with st.status("🛸 2 Milyon Kombinasyon Taranıyor...", expanded=True) as s:
                        frekans = Counter(tum_sayilar)
                        s.write("📈 İstatistiksel ağırlıklar hesaplanıyor...")
                        
                        adaylar = []
                        # 2 MİLYON TARAMA (Süper hızlı döngü)
                        for _ in range(2000000):
                            kolon = tuple(sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet'])))
                            # Puanlama algoritması
                            puan = sum(frekans.get(str(n), 0) for n in kolon)
                            adaylar.append((kolon, puan))
                        
                        s.write("⚖️ En olası kombinasyonlar eleniyor...")
                        adaylar.sort(key=lambda x: x[1], reverse=True)
                        en_iyi_on = adaylar[:10]
                        s.update(label="✅ Hiper Analiz Tamamlandı!", state="complete")

                    for k, (kolon, puan) in enumerate(en_iyi_on, 1):
                        k_str = " - ".join([f"{n:02d}" for n in kolon])
                        st.info(f"**Kolon {k}:** {k_str} (Skor: {puan})")
                    st.balloons()
