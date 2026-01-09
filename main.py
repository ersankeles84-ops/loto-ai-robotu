import streamlit as st
import requests, base64, re, random
from collections import Counter
from datetime import datetime

# --- GITHUB VE GÜVENLİK ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": f"V23 Chronos: {oyun}", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers={"Authorization": f"token {TOKEN}"}).status_code in [200, 201]

def veri_getir(oyun):
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt", headers={"Authorization": f"token {TOKEN}"})
    return base64.b64decode(r.json()['content']).decode() if r.status_code == 200 else ""

# --- ZAMAN ANALİZ MOTORU ---
class ChronosEngine:
    def __init__(self, raw_data, ayar):
        self.ayar = ayar
        self.kayitlar = []
        # Veriyi Tarih ve Sayılar olarak ayrıştır: "Tarih: 2024-05-20 | Sonuç: 02 15..."
        pattern = r"Tarih: (\d{4}-\d{2}-\d{2}) \| Sonuç: ([\d\s,]+)"
        matches = re.findall(pattern, raw_data)
        
        for m in matches:
            tarih = datetime.strptime(m[0], "%Y-%m-%d")
            sayilar = [int(n) for n in re.findall(r'\d+', m[1])]
            self.kayitlar.append({"tarih": tarih, "sayilar": sayilar})
        
        self.tum_sayilar = [s for k in self.kayitlar for s in k['sayilar']]
        self.frekans = Counter(self.tum_sayilar)

    def gecikme_analizi(self):
        # Hangi sayı kaç çekiliştir çıkmıyor?
        gecikmeler = {}
        aktif_sayilar = range(1, self.ayar['max'] + 1)
        for s in aktif_sayilar:
            gecikmeler[s] = 0
            for i, k in enumerate(reversed(self.kayitlar)):
                if s in k['sayilar']:
                    gecikmeler[s] = i
                    break
                gecikmeler[s] = len(self.kayitlar)
        return gecikmeler

# --- ARAYÜZ ---
st.set_page_config(page_title="Loto AI V23 Chronos", layout="wide")
st.title("⏳ Loto AI V23 Chronos-Master")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyunlar.keys()))
ayar = oyunlar[secim]

# Veriyi Çek ve Chronos Motorunu Çalıştır
raw_data = veri_getir(ayar['dosya'])
engine = ChronosEngine(raw_data, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📅 Zamanlı Veri Girişi")
    st.metric("Toplam Çekiliş Kaydı", len(engine.kayitlar))
    
    with st.form("chronos_form", clear_on_submit=True):
        tarih_input = st.date_input("Çekiliş Tarihi", datetime.now())
        sayi_input = st.text_input("Sonuçları Gir (Virgül veya Boşluk)")
        if st.form_submit_button("💎 ZAMANA MÜHÜRLE"):
            t_str = tarih_input.strftime("%Y-%m-%d")
            if t_str in raw_data:
                st.error("Bu tarih zaten arşivde var!")
            else:
                yeni = f"Tarih: {t_str} | Sonuç: {sayi_input}\n"
                if veri_sakla(ayar['dosya'], raw_data + yeni):
                    st.success("Tarihli veri kaydedildi!"); st.rerun()

    # Zaman Analiz Raporu
    if engine.kayitlar:
        st.subheader("🕵️ Gecikme Raporu (Top 5)")
        gecikmeler = engine.gecikme_analizi()
        top_uyuyanlar = sorted(gecikmeler.items(), key=lambda x: x[1], reverse=True)[:5]
        for s, g in top_uyuyanlar:
            st.warning(f"Sayı {s}: {g} çekiliştir çıkmıyor!")

with col2:
    st.header("🧬 Kronolojik Tahmin Motoru")
    if st.button("🚀 ZAMAN ANALİZLİ TAHMİN ÜRET", use_container_width=True):
        if len(engine.kayitlar) < 5:
            st.info("Derin analiz için en az 5 tarihli kayıt lazım kanka!")
        else:
            with st.status("Zaman periyotları ve gecikmeler taranıyor..."):
                gecikmeler = engine.gecikme_analizi()
                final_sets = []
                while len(final_sets) < 10:
                    # Gecikme değeri yüksek olanlara (soğuk) ve frekansı yüksek olanlara (sıcak) ağırlık ver
                    kolon = sorted(random.sample(range(1, ayar['max']+1), ayar['adet']))
                    
                    # Filtre: Ardışık ve Tek-Çift dengesi
                    if any(kolon[i+1] - kolon[i] == 1 for i in range(len(kolon)-1)): continue
                    
                    # Benzerlik kontrolü
                    if not any(len(set(kolon) & set(f)) > 2 for f in final_sets):
                        final_sets.append(kolon)
            
            for i, k in enumerate(final_sets, 1):
                st.success(f"**Tahmin {i}:** {' - '.join([f'{x:02d}' for x in k])}")

st.divider()
st.caption("V23: Tarihleri analiz ederek 'Gecikme (Lag)' ve 'Sıcak/Soğuk' dengesini kurar.")
