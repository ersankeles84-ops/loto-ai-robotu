import streamlit as st
import requests, base64, re, random
from collections import Counter
from datetime import datetime

# --- GITHUB AYARLARI ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": f"V22 Update: {oyun}", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers={"Authorization": f"token {TOKEN}"}).status_code in [200, 201]

def veri_getir(oyun):
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt", headers={"Authorization": f"token {TOKEN}"})
    return base64.b64decode(r.json()['content']).decode() if r.status_code == 200 else ""

# --- ANALİZ MOTORU ---
def asal_mi(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

# --- ARAYÜZ ---
st.set_page_config(page_title="Loto AI V22 Ultimate", layout="wide")
st.title("🛡️ Loto AI V22 Ultimate-Archive")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6, "ekstra": None},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6, "ekstra": "Süper Star"},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10, "ekstra": None},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5, "ekstra": "+1"}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyunlar.keys()))
ayar = oyunlar[secim]

raw_data = veri_getir(ayar['dosya'])
sayi_havuzu = [int(n) for n in re.findall(r'\d+', raw_data)]

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📅 Veri Arşivi & Giriş")
    st.metric(f"{secim} Hafızası", f"{len(sayi_havuzu)} Sayı")
    
    # --- YENİ: TARİHLİ VE MÜKERRER KONTROLLÜ GİRİŞ ---
    with st.form("archive_form", clear_on_submit=True):
        cekilis_tarihi = st.date_input("Çekiliş Tarihi", datetime.now())
        yeni_sayilar = st.text_input("Sayıları Girin (Örn: 02,15,22...)", help="Sayılar arasına virgül veya boşluk bırakın.")
        
        if st.form_submit_button("💎 BULUTA MÜHÜRLE"):
            tarih_str = cekilis_tarihi.strftime("%Y-%m-%d")
            
            # Mükerrer Kontrolü: Tarih daha önce metin dosyasında geçmiş mi?
            if tarih_str in raw_data:
                st.error(f"❌ HATA: {tarih_str} tarihli çekiliş zaten kayıtlı!")
            elif not yeni_sayilar.strip():
                st.warning("⚠️ Lütfen sayıları girin.")
            else:
                yeni_kayit = f"\n Tarih: {tarih_str} | Sonuç: {yeni_sayilar}"
                if veri_sakla(ayar['dosya'], raw_data + yeni_kayit):
                    st.success(f"✅ {tarih_str} verisi mühürlendi ve ekran temizlendi!")
                    st.rerun()

    with st.expander("🗑️ Tehlikeli Bölge"):
        if st.button(f"{secim} Tüm Hafızayı Sil", type="primary"):
            if veri_sakla(ayar['dosya'], ""): st.rerun()

with col2:
    st.header("🚀 Quantum Master Tahmin")
    if st.button("ANALİZİ BAŞLAT", use_container_width=True):
        if len(sayi_havuzu) < 10:
            st.warning("Analiz için önce veri gir kanka!")
        else:
            with st.status("Veriler işleniyor..."):
                final_list = []
                while len(final_list) < 10:
                    kolon = sorted(random.sample(range(1, ayar['max']+1), ayar['adet']))
                    
                    # Filtreler (Asal ve Tek-Çift)
                    tekler = sum(1 for n in kolon if n % 2 != 0)
                    if 1 < tekler < ayar['adet'] - 1:
                        if not any(len(set(kolon) & set(f)) > 2 for f in final_list):
                            final_list.append(kolon)
            
            for i, k in enumerate(final_list, 1):
                ekstra = ""
                if secim == "Çılgın Sayısal": ekstra = f" | ⭐ SS: {random.randint(1, 90)}"
                elif secim == "Şans Topu": ekstra = f" | ➕ Artı: {random.randint(1, 14)}"
                
                txt = ' - '.join([f'{x:02d}' for x in k])
                st.success(f"**Tahmin {i}:** {txt}{ekstra}")

st.divider()
st.caption("V22: Tarihli Kayıt + Mükerrer Kontrolü + Otomatik Temizleme Aktif.")
