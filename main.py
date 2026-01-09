import streamlit as st
import requests, base64, re, random
from collections import Counter
from datetime import datetime
from itertools import combinations

# --- ÇELİK KASA: GITHUB ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": "Sovereign Update", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers={"Authorization": f"token {TOKEN}"}).status_code in [200, 201]

def veri_getir(oyun):
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt", headers={"Authorization": f"token {TOKEN}"})
    return base64.b64decode(r.json()['content']).decode() if r.status_code == 200 else ""

# --- MERKEZİ ANALİZ VE BAĞLANTI MOTORU ---
class SovereignEngine:
    def __init__(self, raw_data, ayar):
        self.ayar = ayar
        # Geçmiş Verileri Tarih ve Sayı Grupları Olarak Ayrıştır
        lines = re.findall(r"Sonuç: ([\d\s,]+)", raw_data)
        self.gecmis_cekilisler = [list(map(int, re.findall(r'\d+', l))) for l in lines]
        self.tum_sayilar = [s for c in self.gecmis_cekilisler for s in c]
        
        # 1. Birliktelik Analizi (Hangi sayılar kanka? Beraber çıkıyorlar?)
        self.baglar = Counter()
        for c in self.gecmis_cekilisler:
            for comb in combinations(sorted(c), 2):
                self.baglar[comb] += 1
                
        # 2. Frekans ve Boşluk (Lag) Analizi
        self.frekans = Counter(self.tum_sayilar)

    def imkansiz_mi(self, kolon):
        # Sayı dizilimleri ve grupları kontrolü
        # A) Çok fazla ardışık (Örn: 1,2,3,4 imkansız dizilimdir)
        if any(kolon[i+2] - kolon[i] == 2 for i in range(len(kolon)-2)): return True
        # B) Toplam Değeri Kontrolü (Sayıların toplamı çok küçük veya çok büyük olamaz)
        toplam = sum(kolon)
        beklenen_ort = (self.ayar['max'] / 2) * self.ayar['adet']
        if not (beklenen_ort * 0.6 < toplam < beklenen_ort * 1.4): return True
        return False

    def zeka_puanla(self, kolon):
        skor = 100
        # Birliktelik puanı ekle (Geçmişte beraber çıkmışlarsa puan artar)
        for comb in combinations(kolon, 2):
            skor += self.baglar.get(comb, 0) * 2
        
        # Tek-Çift Dengesi (İdeal: 3-3 veya 4-2)
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if not (2 <= tekler <= self.ayar['adet'] - 2): skor -= 50
        
        return skor

# --- ARAYÜZ ---
st.set_page_config(page_title="Loto AI Sovereign", layout="wide")
st.title("🏛️ Loto AI: The Sovereign")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6, "ekstra": None},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6, "ekstra": "Süper Star"},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10, "ekstra": None},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5, "ekstra": "+1"}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyunlar.keys()))
ayar = oyunlar[secim]

raw_data = veri_getir(ayar['dosya'])
engine = SovereignEngine(raw_data, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("💾 Veri Ambarı")
    st.metric("Arşivlenen Çekiliş", len(engine.gecmis_cekilisler))
    
    with st.form("sov_form", clear_on_submit=True):
        t = st.date_input("Tarih", datetime.now())
        s = st.text_input("Sonuçlar")
        if st.form_submit_button("💎 MÜHÜRLE"):
            t_s = t.strftime("%Y-%m-%d")
            if t_s in raw_data: st.error("Bu tarih zaten var!")
            else:
                if veri_save := veri_sakla(ayar['dosya'], raw_data + f"\nTarih: {t_s} | Sonuç: {s}"):
                    st.success("Veri mühürlendi!"); st.rerun()

with col2:
    st.header("🧠 Karar Mekanizması")
    if st.button("🚀 TÜM SİSTEMLERİ ÇALIŞTIR", use_container_width=True):
        with st.status("Veri Bağları Analiz Ediliyor..."):
            adaylar = []
            for _ in range(200000):
                k = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
                if not engine.imkansiz_mi(k):
                    skor = engine.zeka_puanla(k)
                    adaylar.append((k, skor))
            
            adaylar.sort(key=lambda x: x[1], reverse=True)
            
            final = []
            for k, s in adaylar:
                if len(final) >= 10: break
                # Benzerlik Savar: Max 1 ortak sayı
                if not any(len(set(k) & set(f[0])) > 1 for f in final):
                    final.append((k, s))

        for i, (k, s) in enumerate(final, 1):
            ekstra = ""
            if secim == "Çılgın Sayısal": ekstra = f" | ⭐ SS: {random.randint(1, 90)}"
            elif secim == "Şans Topu": ekstra = f" | ➕ Artı: {random.randint(1, 14)}"
            st.success(f"**Tahmin {i}:** {' - '.join([f'{x:02d}' for x in k])}{ekstra} (Skor: {s})")

st.divider()
st.caption("Sovereign V1: Birliktelik Matrisi, Tek-Çift Dengesi ve Benzerlik Savar tek bir beyinde birleştirildi.")
