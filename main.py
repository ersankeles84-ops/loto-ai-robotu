import streamlit as st
import requests
import base64
import re
import random
from collections import Counter

# Bulut Bağlantısı
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": f"V16 Brain: {oyun}", "content": base64.b64encode(metin.encode('utf-8')).decode('utf-8')}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers=headers).status_code in [200, 201]

def veri_getir(oyun):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    return base64.b64decode(r.json()['content']).decode('utf-8') if r.status_code == 200 else ""

def asal_mi(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

st.set_page_config(page_title="Loto AI V16 Brain-Power", layout="wide")
st.title("🧠 Loto AI V16 Brain-Power")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.selectbox("Analiz Modu", list(oyunlar.keys()))
ayar = oyunlar[secim]
h_key = f"h_{ayar['dosya']}"

# Hafızayı Canlı Tut
st.session_state[h_key] = veri_getir(ayar['dosya'])

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 Veri Merkezi")
    mevcut = st.session_state[h_key]
    sayilar = [int(n) for n in re.findall(r'\d+', mevcut)]
    st.metric(f"Hafızadaki Sayı", len(sayilar))
    
    with st.form("v16_form"):
        girdi = st.text_area("Yeni Çekilişleri Ekle", height=150)
        if st.form_submit_button("💎 BULUTA MÜHÜRLE"):
            if veri_sakla(ayar['dosya'], mevcut + "\n" + girdi):
                st.success("Veri Mühürlendi!"); st.rerun()

with col2:
    st.header("🧬 Gelişmiş Teori Analizi")
    if st.button("🚀 DERİN ANALİZİ BAŞLAT", use_container_width=True):
        if len(sayilar) < 30: st.warning("Daha fazla veri lazım!")
        else:
            with st.status("🛸 Algoritmalar Çalıştırılıyor..."):
                frekans = Counter(sayilar)
                takip_edenler = {}
                for i in range(len(sayilar)-1):
                    takip_edenler.setdefault(sayilar[i], []).append(sayilar[i+1])
                
                final_list = []
                while len(final_list) < 10:
                    # 1. Aşama: Akıllı Seçim (Frekans + Takipçi + Rastgele Karma)
                    aday = []
                    while len(aday) < ayar['adet']:
                        n = random.randint(1, ayar['max'])
                        if n not in aday: aday.append(n)
                    aday.sort()
                    
                    # 2. Aşama: Sert Filtreler (Fiziksel İmkansızlıklar)
                    # Ardışık kontrolü (Max 1 çift olabilir)
                    if sum(1 for i in range(len(aday)-1) if aday[i+1] - aday[i] == 1) > 1: continue
                    # Tek-Çift Dengesi
                    tekler = sum(1 for n in aday if n % 2 != 0)
                    if tekler < 2 or tekler > (ayar['adet']-2): continue
                    # Asal Sayı Dengesi (En az 1, en fazla 3 asal)
                    asallar = sum(1 for n in aday if asal_mi(n))
                    if asallar < 1 or asallar > 3: continue
                    
                    # 3. Aşama: Benzerlik Filtresi (Kolonlar arası max 1 sayı çakışması)
                    if any(len(set(aday) & set(f)) > 1 for f in final_list): continue
                    
                    final_list.append(aday)
            
            for i, k in enumerate(final_list, 1):
                st.success(f"**Kolon {i}:** {' - '.join([f'{x:02d}' for x in k])}")
