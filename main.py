import streamlit as st
import requests
import base64
import re
import random
from collections import Counter

TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    content_encoded = base64.b64encode(metin.encode('utf-8')).decode('utf-8')
    data = {"message": f"V14 Quantum Kayit: {oyun_adi}", "content": content_encoded}
    if sha: data["sha"] = sha
    res = requests.put(url, json=data, headers=headers)
    return res.status_code in [200, 201]

def veri_getir(oyun_adi):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    return base64.b64decode(r.json()['content']).decode('utf-8') if r.status_code == 200 else ""

st.set_page_config(page_title="Loto AI V14 Quantum Master", layout="wide")
st.title("🌌 Loto AI V14 Quantum Master")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10}, # Seçilen 10 sayı
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.selectbox("Analiz Edilecek Oyun", list(oyunlar.keys()))
ayar = oyunlar[secim]
h_key = f"h_{ayar['dosya']}"

if h_key not in st.session_state:
    st.session_state[h_key] = veri_getir(ayar['dosya'])

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 Veri Havuzu")
    mevcut = st.session_state[h_key]
    sayilar = re.findall(r'\d+', mevcut)
    st.metric(f"{secim} Hafızası", f"{len(sayilar)} Sayı")
    
    with st.form("form_v14", clear_on_submit=True):
        girdi = st.text_area("Yeni Verileri Buraya Ekle", height=150)
        if st.form_submit_button("💎 BULUTA MÜHÜRLE"):
            yeni = mevcut + "\n" + girdi
            if veri_sakla(ayar['dosya'], yeni):
                st.session_state[h_key] = yeni
                st.success("Mühürlendi!")
                st.rerun()

with col2:
    st.header("🧬 Akıllı Filtreleme Algoritması")
    if st.button("🚀 QUANTUM ANALİZİ BAŞLAT", use_container_width=True):
        if len(sayilar) < 10:
            st.warning("Analiz için daha fazla veriye ihtiyaç var!")
        else:
            with st.status("🛸 Analiz ve Filtreleme Başladı..."):
                frekans = Counter(sayilar)
                adaylar = []
                
                for _ in range(2000000): # 2 Milyon deneme
                    kolon = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
                    
                    # 1. Filtre: Mesafe Kontrolü (Sayılar çok bitişik mi?)
                    ardisik_sayisi = sum(1 for i in range(len(kolon)-1) if kolon[i+1] - kolon[i] == 1)
                    if ardisik_sayisi > 1: continue # En fazla 1 tane ardışık çift olabilir
                    
                    # 2. Filtre: Tek/Çift Dengesi (Hepsi tek veya hepsi çift olamaz)
                    tekler = sum(1 for n in kolon if n % 2 != 0)
                    if tekler == 0 or tekler == ayar['adet']: continue
                    
                    # 3. Filtre: Grup Yayılımı (Sayılar tüm tabloya yayılıyor mu?)
                    mesafe = kolon[-1] - kolon[0]
                    if mesafe < (ayar['max'] / 3): continue # Çok dar bir alana sıkışmışsa ele
                    
                    puan = sum(frekans.get(str(n), 0) for n in kolon)
                    adaylar.append((tuple(kolon), puan))
                
                adaylar.sort(key=lambda x: x[1], reverse=True)
                
                # 4. Sert Benzersizlik Filtresi
                final = []
                for k, p in adaylar:
                    if len(final) >= 10: break
                    if not any(len(set(k) & set(f[0])) > 2 for f in final): # Max 2 ortak sayı
                        final.append((k, p))
            
            for i, (k, p) in enumerate(final, 1):
                st.info(f"**Kolon {i}:** {' - '.join([f'{x:02d}' for x in k])}")
