import streamlit as st
import requests, base64, re, random
from collections import Counter
from datetime import datetime

# --- GITHUB ÇELİK KASA BAĞLANTISI ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": f"V25 Iron-Gate: {oyun}", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers={"Authorization": f"token {TOKEN}"}).status_code in [200, 201]

def veri_getir(oyun):
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt", headers={"Authorization": f"token {TOKEN}"})
    if r.status_code == 200:
        return base64.b64decode(r.json()['content']).decode('utf-8')
    return ""

# --- ANA MOTOR VE BEYİN ---
class IronEngine:
    def __init__(self, raw_data, ayar):
        self.ayar = ayar
        # TÜM VERİYİ AYIKLA (Hem tarihli hem düz sayılar)
        self.sayilar = [int(n) for n in re.findall(r'\d+', raw_data)]
        self.frekans = Counter(self.sayilar)
        # Tarihli kayıtları say
        self.kayit_sayisi = len(re.findall(r"Tarih:", raw_data))

    def asal_mi(self, n):
        if n < 2: return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0: return False
        return True

    def analiz_puanla(self, kolon):
        puan = 50 # Baz puan
        # 1. Mesafe/Ardışık Filtresi
        if any(kolon[i+1] - kolon[i] == 1 for i in range(len(kolon)-1)): puan -= 20
        # 2. Tek-Çift Dengesi
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if 2 <= tekler <= (self.ayar['adet'] - 2): puan += 20
        # 3. Asal Sayı Dengesi
        asallar = sum(1 for n in kolon if self.asal_mi(n))
        if 1 <= asallar <= 3: puan += 15
        # 4. Frekans (Sıcaklık) Etkisi
        f_skor = sum(self.frekans.get(n, 0) for n in kolon)
        puan += (f_skor / 100)
        return puan

# --- ARAYÜZ ---
st.set_page_config(page_title="Loto AI V25 Iron-Gate", layout="wide")
st.title("🛡️ Loto AI V25 Iron-Gate")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyunlar.keys()))
ayar = oyunlar[secim]

# KRİTİK ADIM: VERİYİ ÇEK VE MOTORU KUR
raw_data = veri_getir(ayar['dosya'])
engine = IronEngine(raw_data, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📥 Veri ve Arşiv")
    st.success(f"Bulut Hafızası: {len(engine.sayilar)} Sayı Aktif!")
    st.info(f"Tarihli Kayıt Sayısı: {engine.kayit_sayisi}")
    
    with st.form("input_form", clear_on_submit=True):
        t_in = st.date_input("Çekiliş Tarihi", datetime.now())
        s_in = st.text_input("Sonuçları Gir (Virgül/Boşluk)")
        if st.form_submit_button("💎 BULUTA MÜHÜRLE"):
            t_str = t_in.strftime("%Y-%m-%d")
            if t_str in raw_data:
                st.error("Bu tarih zaten kayıtlı!")
            elif not s_in.strip():
                st.warning("Veri girmedin kanka!")
            else:
                yeni = f"\nTarih: {t_str} | Sonuç: {s_in}"
                if veri_sakla(ayar['dosya'], raw_data + yeni):
                    st.rerun()

with col2:
    st.header("🧠 Merkezi Beyin Analizi")
    if st.button("🚀 TAHMİN HAVUZUNU OLUŞTUR", use_container_width=True):
        if len(engine.sayilar) < 10:
            st.warning("Hafıza boş görünüyor, lütfen veri ekle!")
        else:
            with st.status("Algoritmalar Çarpıştırılıyor..."):
                adaylar = []
                for _ in range(150000): # 150 bin deneme
                    kolon = sorted(random.sample(range(1, ayar['max']+1), ayar['adet']))
                    skor = engine.analiz_puanla(kolon)
                    adaylar.append((kolon, skor))
                
                adaylar.sort(key=lambda x: x[1], reverse=True)
                final = []
                for k, s in adaylar:
                    if len(final) >= 10: break
                    if not any(len(set(k) & set(f[0])) > 2 for f in final):
                        final.append((k, s))

            for i, (k, s) in enumerate(final, 1):
                # Ekstra sayı kuralları
                ekstra = ""
                if secim == "Çılgın Sayısal": ekstra = f" | ⭐ SS: {random.randint(1, 90)}"
                elif secim == "Şans Topu": ekstra = f" | ➕ Artı: {random.randint(1, 14)}"
                
                txt = ' - '.join([f'{x:02d}' for x in k])
                st.success(f"**Tahmin {i}:** {txt}{ekstra} (Güç: {s:.1f})")

st.divider()
st.caption("Iron-Gate V25: Veri okuma garantisi + Otomatik temizleme + Merkezi beyin puanlaması.")
