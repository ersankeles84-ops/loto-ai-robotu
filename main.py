import streamlit as st
import requests, base64, re, random
from collections import Counter
from datetime import datetime

# --- GÜVENLİK VE BULUT BAĞLANTISI ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": f"V26 Supreme Update", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers={"Authorization": f"token {TOKEN}"}).status_code in [200, 201]

def veri_getir(oyun):
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt", headers={"Authorization": f"token {TOKEN}"})
    return base64.b64decode(r.json()['content']).decode('utf-8') if r.status_code == 200 else ""

# --- SUPREME ANALİZ MOTORU ---
class SupremeBrain:
    def __init__(self, raw_data, ayar):
        self.ayar = ayar
        self.raw = raw_data
        # EVRENSEL AYIKLAYICI: Dosyadaki her rakamı çeker
        self.sayilar = [int(n) for n in re.findall(r'\d+', raw_data) if 0 < int(n) <= ayar['max']]
        self.frekans = Counter(self.sayilar)

    def puanla(self, kolon):
        puan = 50.0
        # 1. Mesafe ve Ardışıklık
        if any(kolon[i+1] - kolon[i] == 1 for i in range(len(kolon)-1)): puan -= 15
        # 2. Tek-Çift Dengesi
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if 2 <= tekler <= (self.ayar['adet'] - 2): puan += 20
        # 3. Frekans Uyumu
        puan += sum(self.frekans.get(n, 0) for n in kolon) / 10
        return round(puan, 1)

# --- ARAYÜZ ---
st.set_page_config(page_title="Loto AI V26 Supreme", layout="wide")
st.title("🚀 Loto AI V26 Final-Supreme")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6, "ekstra": None},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6, "ekstra": "Süper Star"},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10, "ekstra": None},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5, "ekstra": "+1"}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyunlar.keys()))
ayar = oyunlar[secim]

# Veri Akışını Başlat
raw_content = veri_getir(ayar['dosya'])
brain = SupremeBrain(raw_content, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 Veri Merkezi")
    st.success(f"Aktif Hafıza: {len(brain.sayilar)} Sayı")
    
    with st.form("supreme_input", clear_on_submit=True):
        tarih = st.date_input("Çekiliş Tarihi", datetime.now())
        girdi = st.text_area("Yeni Çekilişleri Ekle")
        if st.form_submit_button("💎 BULUTA MÜHÜRLE VE TEMİZLE"):
            if tarih.strftime("%Y-%m-%d") in raw_content:
                st.error("Bu tarih zaten kayıtlı!")
            elif girdi.strip():
                yeni_veri = f"{raw_content}\nTarih: {tarih.strftime('%Y-%m-%d')} | Sonuç: {girdi}"
                if veri_sakla(ayar['dosya'], yeni_veri): st.rerun()

with col2:
    st.header("🧬 Supreme Tahmin Çıktısı")
    if st.button("🚀 MASTER ANALİZİ BAŞLAT", use_container_width=True):
        with st.status("Milyonlarca Olasılık Eleniyor..."):
            havuz = []
            for _ in range(100000):
                kolon = sorted(random.sample(range(1, ayar['max']+1), ayar['adet']))
                skor = brain.puanla(kolon)
                havuz.append((kolon, skor))
            
            havuz.sort(key=lambda x: x[1], reverse=True)
            final_10 = []
            for k, s in havuz:
                if len(final_10) >= 10: break
                if not any(len(set(k) & set(f[0])) > 2 for f in final_10): # Benzerlik filtresi
                    final_10.append((k, s))

        for i, (k, s) in enumerate(final_10, 1):
            ekstra_str = ""
            if secim == "Çılgın Sayısal": ekstra_str = f" | ⭐ SS: {random.randint(1, 90)}"
            elif secim == "Şans Topu": ekstra_str = f" | ➕ Artı: {random.randint(1, 14)}"
            
            res_txt = ' - '.join([f'{x:02d}' for x in k])
            st.info(f"**Tahmin {i}:** {res_txt}{ekstra_str} (Güç: %{s})")
