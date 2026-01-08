import streamlit as st
import requests
import base64
import re
import random
from collections import Counter

# Bulut Bağlantısı - Secrets
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO = st.secrets["REPO_NAME"]
except:
    st.error("❌ HATA: Secrets ayarların eksik kanka! GITHUB_TOKEN ve REPO_NAME ekli mi?")

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # Mevcut dosyayı kontrol et
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    
    content_encoded = base64.b64encode(metin.encode('utf-8')).decode('utf-8')
    data = {"message": f"V10 Kayit: {oyun_adi}", "content": content_encoded}
    if sha: data["sha"] = sha
    
    res = requests.put(url, json=data, headers=headers)
    if res.status_code in [200, 201]: return True
    else:
        st.error(f"GitHub Hatası: {res.status_code} - {res.text}")
        return False

def veri_getir(oyun_adi):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return base64.b64decode(r.json()['content']).decode('utf-8')
    return ""

st.set_page_config(page_title="Loto AI V10 Master", layout="wide")
st.title("🏆 Loto AI Hyper Master V10.0")

oyun_ayarlar = {
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 22},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

tabs = st.tabs(list(oyun_ayarlar.keys()))

for i, tab in enumerate(tabs):
    isim = list(oyun_ayarlar.keys())[i]
    ayar = oyun_ayarlar[isim]
    h_key = f"h_{ayar['dosya']}"
    
    with tab:
        # OTOMATİK VERİ ÇEKME
        if h_key not in st.session_state or not st.session_state[h_key]:
            st.session_state[h_key] = veri_getir(ayar['dosya'])

        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.header("📊 Veri Yönetimi")
            mevcut = st.session_state[h_key]
            tum_sayilar = re.findall(r'\d+', mevcut)
            st.metric("Kayıtlı Sayı Havuzu", len(tum_sayilar))
            
            with st.form(key=f"v10_form_{ayar['dosya']}", clear_on_submit=True):
                girdi = st.text_area("Verileri Yapıştır", height=200)
                if st.form_submit_button("💎 BULUTA MÜHÜRLE"):
                    if girdi:
                        yeni_hafiza = mevcut + "\n" + girdi
                        if veri_sakla(ayar['dosya'], yeni_hafiza):
                            st.session_state[h_key] = yeni_hafiza
                            st.success("✅ Hafıza Buluta Çakıldı!")
                            st.rerun()

        with col2:
            st.header("🧬 Akıllı Analiz (2 Milyon)")
            if st.button(f"🚀 MASTER ANALİZİ BAŞLAT", key=f"v10_btn_{ayar['dosya']}", use_container_width=True):
                if len(tum_sayilar) < 10:
                    st.warning("Hafıza boş kanka, veri yükle!")
                else:
                    with st.status("🛸 2 Milyon Olasılık Taranıyor...", expanded=True):
                        frekans = Counter(tum_sayilar)
                        adaylar = []
                        # 2 MİLYONLUK DEV DÖNGÜ
                        for _ in range(2000000):
                            kolon = tuple(sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet'])))
                            puan = sum(frekans.get(str(n), 0) for n in kolon)
                            adaylar.append((kolon, puan))
                        
                        adaylar.sort(key=lambda x: x[1], reverse=True)
                        
                        # V10 FİLTRE: ARDIŞIKLIĞI VE BENZERLİĞİ ÖNLE
                        final_on = []
                        for kolon, puan in adaylar:
                            if len(final_on) >= 10: break
                            # Diğer seçilen kolonlarla çok benzer olmasın
                            cok_benzer = any(len(set(kolon) & set(f[0])) > 3 for f in final_on)
                            # 3'ten fazla ardışık sayı olmasın (01-02-03-04 gibi)
                            ardisik = sum(1 for j in range(len(kolon)-1) if kolon[j+1] - kolon[j] == 1)
                            
                            if not cok_benzer and ardisik < 3:
                                final_on.append((kolon, puan))

                    for k, (kolon, puan) in enumerate(final_on, 1):
                        k_str = " - ".join([f"{n:02d}" for n in kolon])
                        st.success(f"**Kolon {k}:** {k_str} (Skor: {puan})")
                    st.balloons()
