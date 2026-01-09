import streamlit as st
import requests, base64, re, random
from collections import Counter

# --- GITHUB AYARLARI ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": f"V20 Master: {oyun}", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers={"Authorization": f"token {TOKEN}"}).status_code in [200, 201]

def veri_getir(oyun):
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt", headers={"Authorization": f"token {TOKEN}"})
    return base64.b64decode(r.json()['content']).decode() if r.status_code == 200 else ""

# --- OYUN KURALLARI MOTORU ---
oyun_kurallari = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6, "ekstra": None},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6, "ekstra": "Süper Star (1-90)"},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10, "ekstra": None},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5, "ekstra": "+1 (1-14)"}
}

st.set_page_config(page_title="Loto AI V20 Master", layout="wide")
st.title("🌌 Loto AI V20 Master - Profesyonel")

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyun_kurallari.keys()))
ayar = oyun_kurallari[secim]

# Veri Akışı
raw_data = veri_getir(ayar['dosya'])
sayi_havuzu = [int(n) for n in re.findall(r'\d+', raw_data)]
frekans = Counter(sayi_havuzu)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 Veri ve Hafıza")
    st.metric(f"{secim} Kayıtlı Sayı", len(sayi_havuzu))
    
    # Otomatik Temizlenen Form
    with st.form("master_form", clear_on_submit=True):
        girdi = st.text_area("Yeni Çekilişleri Ekle", height=150)
        if st.form_submit_button("💎 BULUTA MÜHÜRLE", use_container_width=True):
            if girdi.strip():
                if veri_sakla(ayar['dosya'], raw_data + "\n" + girdi):
                    st.success("Veri mühürlendi, ekran temizlendi!"); st.rerun()

with col2:
    st.header(f"🧬 {secim} Akıllı Analiz")
    if st.button("🚀 MASTER ANALİZİ BAŞLAT", use_container_width=True):
        with st.status("Kuantum Olasılıklar Hesaplanıyor..."):
            tahminler = []
            for _ in range(10):
                # Ana Sayılar
                kolon = sorted(random.sample(range(1, ayar['max']+1), ayar['adet']))
                
                # Ekstra Sayı Kuralları (Süper Star veya +1)
                ekstra_bilgi = ""
                if secim == "Çılgın Sayısal":
                    super_star = random.randint(1, 90)
                    ekstra_bilgi = f" | ⭐ Süper Star: {super_star}"
                elif secim == "Şans Topu":
                    plus_one = random.randint(1, 14)
                    ekstra_bilgi = f" | ➕ Artı: {plus_one}"
                
                tahminler.append(f"{' - '.join([f'{x:02d}' for x in kolon])}{ekstra_bilgi}")

            for i, t in enumerate(tahminler, 1):
                st.success(f"**Kolon {i}:** {t}")

st.sidebar.divider()
st.sidebar.info(f"**Oyun Kuralları:**\n- Küre: 1-{ayar['max']}\n- Seçilecek: {ayar['adet']}\n- Ekstra: {ayar['ekstra'] if ayar['ekstra'] else 'Yok'}")
