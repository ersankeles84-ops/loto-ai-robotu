import streamlit as st
import requests
import base64
import re
import random
from collections import Counter

# Bulut Bağlantı Ayarları
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    content_encoded = base64.b64encode(metin.encode('utf-8')).decode('utf-8')
    data = {"message": f"V12 Ultra Kayit: {oyun_adi}", "content": content_encoded}
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

st.set_page_config(page_title="Loto AI V12 Ultra Master", layout="wide")
st.title("🏆 Loto AI Ultra Master V12")

# Oyun Limitleri
oyun_ayar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90}
}

secim = st.selectbox("Analiz Edilecek Oyun", list(oyun_ayar.keys()))
ayar = oyun_ayar[secim]
h_key = f"h_{ayar['dosya']}"

# --- KALICILIK ÇÖZÜMÜ ---
# Her sayfa açıldığında veya oyun değiştiğinde GitHub'dan taze veriyi çek
st.session_state[h_key] = veri_getir(ayar['dosya'])

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 Veri Havuzu")
    mevcut_veri = st.session_state[h_key]
    sayi_havuzu = re.findall(r'\d+', mevcut_veri)
    st.metric("Buluttaki Kayıtlı Sayı", len(sayi_havuzu))
    
    with st.form("veri_yukle", clear_on_submit=True):
        girdi = st.text_area("Yeni Çekilişleri Buraya Ekle", height=150)
        if st.form_submit_button("💎 BULUTA MÜHÜRLE"):
            yeni_metin = mevcut_veri + "\n" + girdi
            if veri_sakla(ayar['dosya'], yeni_metin):
                st.session_state[h_key] = yeni_metin
                st.success("Veri GitHub'a mühürlendi! Artık sıfırlanmaz.")
                st.rerun()

with col2:
    st.header("🧬 Ultra Analiz (2 Milyon)")
    if st.button("🚀 ANALİZİ BAŞLAT", use_container_width=True):
        if len(sayi_havuzu) < 10: st.warning("Hafıza boş kanka!")
        else:
            with st.status("🛸 2 Milyon Olasılık Taranıyor ve Filtreleniyor..."):
                frekans = Counter(sayi_havuzu)
                adaylar = []
                for _ in range(2000000):
                    kolon = tuple(sorted(random.sample(range(1, ayar['max'] + 1), 6)))
                    
                    # --- V12 ARDIŞIK VE BENZERLİK FİLTRELERİ ---
                    # 1. Filtre: Yan yana 2'den fazla ardışık sayı gelmesin (Örn: 10-11-12 YASAK)
                    ardisik_hata = any(kolon[i+1] - kolon[i] == 1 and kolon[i+2] - kolon[i+1] == 1 for i in range(4))
                    
                    # 2. Filtre: Kolon içinde çok fazla ardışık çift olmasın
                    cift_ardisik = sum(1 for i in range(5) if kolon[i+1] - kolon[i] == 1)
                    
                    if not ardisik_hata and cift_ardisik <= 1:
                        puan = sum(frekans.get(str(n), 0) for n in kolon)
                        adaylar.append((kolon, puan))
                
                adaylar.sort(key=lambda x: x[1], reverse=True)
                final_list = []
                for k, p in adaylar:
                    if len(final_list) >= 10: break
                    # 3. Filtre: Tahmin edilen kolonlar birbirine benzemesin (Max 2 sayı çakışabilir)
                    if not any(len(set(k) & set(f[0])) > 2 for f in final_list):
                        final_list.append((k, p))
            
            for i, (k, p) in enumerate(final_list, 1):
                st.info(f"**Tahmin {i}:** {' - '.join([f'{x:02d}' for x in k])} (Güç: %{min(100, p//10)})")
