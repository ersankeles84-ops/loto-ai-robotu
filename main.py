import streamlit as st
import requests
import base64
import re
import random
from collections import Counter

# Bulut Bağlantısı - Secrets
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun_adi, metin):
    try:
        url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
        headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
        r = requests.get(url, headers=headers)
        sha = r.json()['sha'] if r.status_code == 200 else None
        content_encoded = base64.b64encode(metin.encode('utf-8')).decode('utf-8')
        data = {"message": f"V10 Master Update: {oyun_adi}", "content": content_encoded}
        if sha: data["sha"] = sha
        res = requests.put(url, json=data, headers=headers)
        return res.status_code in [200, 201]
    except: return False

def veri_getir(oyun_adi):
    try:
        url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
        headers = {"Authorization": f"token {TOKEN}"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return base64.b64decode(r.json()['content']).decode('utf-8')
    except: pass
    return ""

st.set_page_config(page_title="Loto AI V10.0 Master", layout="wide")
st.title("🏆 Loto AI Hyper Master V10.0")
st.subheader("2 Milyon Kombinasyon | Akıllı Filtreleme | Kalıcı Hafıza")

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
        # Otomatik Hafıza Kontrolü
        if h_key not in st.session_state or not st.session_state[h_key]:
            st.session_state[h_key] = veri_getir(ayar['dosya'])

        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.header("📊 Veri Yönetimi")
            mevcut = st.session_state[h_key]
            tum_sayilar = re.findall(r'\d+', mevcut)
            st.metric("Kayıtlı Sayı Havuzu", len(tum_sayilar))
            
            with st.form(key=f"v10_f_{ayar['dosya']}", clear_on_submit=True):
                girdi = st.text_area("Yeni Çekilişleri Buraya Yapıştır", height=200, help="Tarih ve sayıları birlikte girebilirsin.")
                if st.form_submit_button("💎 BULUTA MÜHÜRLE"):
                    if girdi:
                        yeni_veri = mevcut + "\n" + girdi
                        if veri_sakla(ayar['dosya'], yeni_veri):
                            st.session_state[h_key] = yeni_veri
                            st.success("Hafıza V10 seviyesine güncellendi!")
                            st.rerun()
                        else: st.error("Bağlantı hatası!")

        with col2:
            st.header("🧬 V10 Analiz Motoru (2M)")
            if st.button(f"🚀 MASTER ANALİZİ BAŞLAT", key=f"v10_b_{ayar['dosya']}", use_container_width=True):
                if len(tum_sayilar) < 20:
                    st.warning("Analiz için daha fazla veriye açım kanka!")
                else:
                    with st.status("🛸 2.000.000 Kombinasyon Taranıyor...", expanded=True) as status:
                        frekans = Counter(tum_sayilar)
                        adaylar = []
                        
                        # 2 MİLYONLUK DEV DÖNGÜ
                        for _ in range(2000000):
                            kolon = tuple(sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet'])))
                            # Puanlama: Geçmiş uyumu + Rastgelelik (Kaos Faktörü)
                            puan = sum(frekans.get(str(n), 0) for n in kolon)
                            adaylar.append((kolon, puan))
                        
                        adaylar.sort(key=lambda x: x[1], reverse=True)
                        
                        # V10 AKILLI ÇEŞİTLİLİK FİLTRESİ
                        final_on = []
                        for kolon, puan in adaylar:
                            if len(final_on) >= 10: break
                            # Filtre: Ardışık sayıları dengele ve diğer kolonlara benzemesin
                            benzerlik_var = any(len(set(kolon) & set(f[0])) > 3 for f in final_on)
                            ardisik_sayisi = sum(1 for j in range(len(kolon)-1) if kolon[j+1] - kolon[j] == 1)
                            
                            if not benzerlik_var and ardisik_sayisi < 3:
                                final_on.append((kolon, puan))
                        
                        status.update(label="✅ V10 Analizi Başarıyla Tamamlandı!", state="complete")

                    st.subheader("🎯 Stratejik En Güçlü 10 Kolon")
                    for k, (kolon, puan) in enumerate(final_on, 1):
                        k_str = " - ".join([f"{n:02d}" for n in kolon])
                        st.success(f"**Kolon {k}:** {k_str} (Analiz Skoru: {puan})")
                    st.balloons()
