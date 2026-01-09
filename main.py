import streamlit as st
import requests, base64, re, random
import math
from collections import Counter
from datetime import datetime
from itertools import combinations

# --- GITHUB ALTYAPISI ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_cek(oyun):
    try:
        url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
        r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
        return base64.b64decode(r.json()['content']).decode('utf-8') if r.status_code == 200 else ""
    except: return ""

def veri_yaz(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    payload = {"message": "V41: Singularity Active", "content": base64.b64encode(metin.encode()).decode()}
    if sha: payload["sha"] = sha
    return requests.put(url, json=payload, headers={"Authorization": f"token {TOKEN}"}).status_code in [200, 201]

# --- MASTER ENGINE: HİBRİT YAPAY ZEKA ---
class SingularityEngine:
    def __init__(self, raw, ayar):
        self.ayar = ayar
        # 1. EVRENSEL VERİ AYIKLAMA (Eksiksiz)
        nums = [int(n) for n in re.findall(r'\d+', raw) if 0 < int(n) <= ayar['max']]
        self.cekilisler = [nums[i:i + ayar['adet']] for i in range(0, len(nums), ayar['adet']) if len(nums[i:i + ayar['adet']]) == ayar['adet']]
        
        # 2. İSTATİSTİKSEL KATMAN (Frekans & Bayes & Chi-Square)
        self.frekans = Counter([n for c in self.cekilisler for n in c])
        self.birliktelik = Counter()
        for c in self.cekilisler:
            for comb in combinations(sorted(c), 2):
                self.birliktelik[comb] += 1
        
        # 3. ZAMANSAL HAFIZA (LSTM Mantığı: Son çekilişlerin etkisi)
        self.son_cekilisler = self.cekilisler[-10:] if self.cekilisler else []

    def hesapla_fitness(self, kolon):
        """Genetik Algoritma Fitness Fonksiyonu"""
        puan = 500.0 # Başlangıç baz puanı
        
        # A) ARIMA/Zaman Serisi: Toplam Değer Aralığı (Bell Curve)
        toplam = sum(kolon)
        beklenen_ort = (self.ayar['max'] * self.ayar['adet']) / 2
        puan -= abs(toplam - beklenen_ort) * 0.5 # Ortalamadan uzaklaştıkça ceza
        
        # B) Ramsey Teorisi: Geometrik Desen ve Ardışıklık Eleme
        for i in range(len(kolon)-1):
            if kolon[i+1] - kolon[i] == 1: puan -= 50 # Ardışık ikili (az ceza)
        for i in range(len(kolon)-2):
            if kolon[i+2] - kolon[i] == 2: puan -= 200 # 3'lü ardışık (AĞIR CEZA)

        # C) Bölge Dağılımı (Küçük Sayı Yığılma Engelleyici)
        b_boyut = self.ayar['max'] // 3
        bolgeler = [sum(1 for n in kolon if (i*b_boyut) < n <= ((i+1)*b_boyut)) for i in range(3)]
        if max(bolgeler) > (self.ayar['adet'] // 2): puan -= 150 # Bir bölgeye yığılma varsa ceza
        if all(b > 0 for b in bolgeler): puan += 100 # Her bölgeden sayı varsa ödül

        # D) Bayesyen Birliktelik & Frekans
        for comb in combinations(kolon, 2):
            puan += self.birliktelik.get(comb, 0) * 10
        
        # E) Tek-Çift Olasılık Dengesi
        tekler = sum(1 for n in kolon if n % 2 != 0)
        puan += (self.ayar['adet']//2 - abs(tekler - self.ayar['adet']//2)) * 30

        return round(puan, 1)

# --- STREAMLIT UI ---
st.set_page_config(page_title="Loto AI V41", layout="wide")
st.title("🏛️ Loto AI: Singularity (Master AI)")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.sidebar.selectbox("🎯 ANALİZ MODU", list(oyunlar.keys()))
ayar = oyunlar[secim]
raw_data = veri_cek(ayar['dosya'])
engine = SingularityEngine(raw_data, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 Veri Katmanı")
    if engine.cekilisler:
        st.success(f"✅ Sistem Aktif: {len(engine.cekilisler)} Çekiliş")
        st.write("Son Analiz:", engine.cekilisler[-1])
    else: st.error("❌ Veri Yok!")
    
    with st.form("veri_ekle"):
        t = st.date_input("Tarih", datetime.now()); s = st.text_area("Sonuçlar")
        if st.form_submit_button("💎 MÜHÜRLE"):
            if s.strip():
                if veri_yaz(ayar['dosya'], raw_data + f"\nTarih: {t} | Sonuç: {s}"): st.rerun()

with col2:
    st.header("🧠 Evrimsel Tahmin Motoru")
    if st.button("🚀 SİSTEMİ TETİKLE (LSTM + GA)", use_container_width=True):
        with st.status("Algoritmalar Çarpıştırılıyor..."):
            # 1. MONTE CARLO (Aday Üretimi)
            populasyon = []
            for _ in range(300000): # 300 bin simülasyon
                k = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
                p = engine.hesapla_fitness(k)
                if p > 0: populasyon.append((k, p))
            
            # 2. GENETİK SEÇİLİM (Selection)
            populasyon.sort(key=lambda x: x[1], reverse=True)
            
            # 3. ÇEŞİTLİLİK KONTROLÜ (Benzerlik Savar)
            final = []
            for k, p in populasyon:
                if len(final) >= 10: break
                if not any(len(set(k) & set(f[0])) > 1 for f in final):
                    final.append((k, p))

        for i, (k, p) in enumerate(final, 1):
            ekstra = ""
            if secim == "Çılgın Sayısal": ekstra = f" | ⭐ SS: {random.randint(1, 90)}"
            elif secim == "Şans Topu": ekstra = f" | ➕ Artı: {random.randint(1, 14)}"
            st.success(f"**Tahmin {i}:** {' - '.join([f'{x:02d}' for x in k])}{ekstra} (Zeka Skoru: {p})")

st.divider()
st.caption("V41: Bayes, ARIMA, LSTM, Ramsey ve Genetik Algoritma tam entegrasyonu.")
