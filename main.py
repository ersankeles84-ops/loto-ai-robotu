import streamlit as st
import requests, base64, re, random
from collections import Counter
from datetime import datetime

# --- GITHUB BAĞLANTI PROTOKOLÜ ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": f"V24 Neural Update: {oyun}", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers={"Authorization": f"token {TOKEN}"}).status_code in [200, 201]

def veri_getir(oyun):
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt", headers={"Authorization": f"token {TOKEN}"})
    return base64.b64decode(r.json()['content']).decode() if r.status_code == 200 else ""

# --- MERKEZİ BEYİN ALGORİTMALARI ---
class BrainEngine:
    def __init__(self, raw_data, ayar):
        self.ayar = ayar
        # Tarihli verileri ayıkla
        matches = re.findall(r"Tarih: (\d{4}-\d{2}-\d{2}) \| Sonuç: ([\d\s,]+)", raw_data)
        self.cekilisler = [list(map(int, re.findall(r'\d+', m[1]))) for m in matches]
        self.tum_sayilar = [s for c in self.cekilisler for s in c]
        self.frekans = Counter(self.tum_sayilar)

    def asal_mi(self, n):
        if n < 2: return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0: return False
        return True

    def analiz_puanla(self, kolon):
        puan = 0
        # 1. Mesafe ve Ardışık Analizi
        ardisik = sum(1 for i in range(len(kolon)-1) if kolon[i+1] - kolon[i] == 1)
        if ardisik == 0: puan += 30
        elif ardisik == 1: puan += 15
        
        # 2. Tek-Çift Dengesi
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if 2 <= tekler <= (self.ayar['adet'] - 2): puan += 25
        
        # 3. Asal Sayı Dağılımı
        asallar = sum(1 for n in kolon if self.asal_mi(n))
        if 1 <= asallar <= 3: puan += 20
        
        # 4. Frekans Uyumu (Sıcak/Soğuk Karışımı)
        f_puan = sum(self.frekans.get(n, 0) for n in kolon)
        puan += (f_puan / (len(self.cekilisler) if self.cekilisler else 1))
        
        return puan

# --- ARAYÜZ ---
st.set_page_config(page_title="Loto AI V24 Neural-Master", layout="wide")
st.title("🧠 Loto AI V24 Neural-Master")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyunlar.keys()))
ayar = oyunlar[secim]

# Veriyi Çek ve Beyne Gönder
raw_data = veri_getir(ayar['dosya'])
beyin = BrainEngine(raw_data, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📥 Veri Kayıt Merkezi")
    st.metric("Arşivdeki Çekiliş Sayısı", len(beyin.cekilisler))
    
    with st.form("neural_form", clear_on_submit=True):
        t_input = st.date_input("Çekiliş Tarihi", datetime.now())
        s_input = st.text_input("Sonuçları Gir")
        if st.form_submit_button("💎 MÜHÜRLE VE TEMİZLE"):
            t_str = t_input.strftime("%Y-%m-%d")
            if t_str in raw_data: st.error("Bu tarih kayıtlı!")
            else:
                yeni = f"Tarih: {t_str} | Sonuç: {s_input}\n"
                if veri_sakla(ayar['dosya'], raw_data + yeni):
                    st.success("Kaydedildi!"); st.rerun()

with col2:
    st.header("🔮 Merkezi Beyin Tahminleri")
    if st.button("🚀 TÜM ALGORİTMALARI ÇALIŞTIR", use_container_width=True):
        if len(beyin.cekilisler) < 3:
            st.warning("Beynin analiz yapabilmesi için daha fazla tarihli veriye ihtiyacı var!")
        else:
            with st.status("Algoritmalar çarpıştırılıyor, Merkezi Beyin karar veriyor..."):
                adaylar = []
                # Milyonlarca kombinasyon arasından beyin en iyileri ayıklar
                for _ in range(200000):
                    kolon = sorted(random.sample(range(1, ayar['max']+1), ayar['adet']))
                    score = beyin.analiz_puanla(kolon)
                    adaylar.append((kolon, score))
                
                # Puanı en yüksek olanları seç
                adaylar.sort(key=lambda x: x[1], reverse=True)
                
                final_sets = []
                for k, s in adaylar:
                    if len(final_sets) >= 10: break
                    # Çeşitlilik (Sert benzerlik filtresi)
                    if not any(len(set(k) & set(f[0])) > 2 for f in final_sets):
                        final_sets.append((k, s))
            
            for i, (k, s) in enumerate(final_sets, 1):
                # Oyun kurallarına göre ekstra sayılar
                ekstra = ""
                if secim == "Çılgın Sayısal": ekstra = f" | ⭐ SS: {random.randint(1, 90)}"
                elif secim == "Şans Topu": ekstra = f" | ➕ Artı: {random.randint(1, 14)}"
                
                txt = ' - '.join([f'{x:02d}' for x in k])
                st.success(f"**Tahmin {i}:** {txt}{ekstra} (Zeka Skoru: {s:.2f})")

st.divider()
st.caption("V24: Tüm istatistiksel alt modeller merkezi bir puanlama algoritmasında birleştirildi.")
