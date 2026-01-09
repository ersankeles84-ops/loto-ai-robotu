import streamlit as st
import requests, base64, re, random
from collections import Counter
from datetime import datetime
from itertools import combinations

# --- GITHUB KİMLİK DOĞRULAMA ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_cek(oyun):
    try:
        url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
        r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
        if r.status_code == 200:
            return base64.b64decode(r.json()['content']).decode('utf-8')
    except: pass
    return ""

def veri_yaz(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    payload = {"message": "V36: Absolute Security", "content": base64.b64encode(metin.encode()).decode()}
    if sha: payload["sha"] = sha
    return requests.put(url, json=payload, headers={"Authorization": f"token {TOKEN}"}).status_code in [200, 201]

# --- ÜST DÜZEY ANALİZ MERKEZİ ---
class AbsoluteEngine:
    def __init__(self, raw, ayar):
        self.ayar = ayar
        # RADİKAL VERİ OKUMA: Her şeyi rakama çevir
        nums = list(map(int, re.findall(r'\d+', raw)))
        self.cekilisler = [nums[i:i + ayar['adet']] for i in range(0, len(nums), ayar['adet']) if len(nums[i:i + ayar['adet']]) == ayar['adet']]
        
        # Birliktelik (Coupling) ve Frekans
        self.baglar = Counter()
        for c in self.cekilisler:
            for comb in combinations(sorted(c), 2):
                self.baglar[comb] += 1
        self.frekans = Counter([n for c in self.cekilisler for n in c])

    def skorla(self, k):
        p = 100.0
        # 1. Bölge Dağılımı (Küçük Sayı Yığılma Engelleyici)
        b1 = sum(1 for n in k if n <= (self.ayar['max'] // 3))
        b2 = sum(1 for n in k if (self.ayar['max'] // 3) < n <= (self.ayar['max'] // 3 * 2))
        b3 = sum(1 for n in k if n > (self.ayar['max'] // 3 * 2))
        if max(b1, b2, b3) > 3: p -= 60
        
        # 2. Tek-Çift ve Ardışıklık Dengesi
        if sum(1 for n in k if n % 2 != 0) in [0, self.ayar['adet']]: p -= 50
        if any(k[i+2] - k[i] == 2 for i in range(len(k)-2)): p -= 80 # 3'lü ardışık blokaj
        
        # 3. Tarihsel Birliktelik
        for comb in combinations(k, 2):
            p += self.baglar.get(comb, 0) * 6
        return round(p, 1)

# --- ARAYÜZ ---
st.set_page_config(page_title="Loto AI V36 Absolute", layout="wide")
st.title("🏆 Loto AI V36: The Absolute")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.sidebar.selectbox("🎯 OYUN", list(oyunlar.keys()))
ayar = oyunlar[secim]
raw_data = veri_cek(ayar['dosya'])
engine = AbsoluteEngine(raw_data, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📋 Veri Kasası")
    if engine.cekilisler:
        st.success(f"✅ {len(engine.cekilisler)} Çekiliş Aktif!")
        st.write("Son Veri:", engine.cekilisler[-1])
    else: st.error("❌ Veri Yok!")
    
    with st.form("ekle"):
        t = st.date_input("Tarih", datetime.now())
        s = st.text_input("Sonuçlar")
        if st.form_submit_button("💎 MÜHÜRLE"):
            if veri_yaz(ayar['dosya'], raw_data + f"\nTarih: {t} | Sonuç: {s}"): st.rerun()

with col2:
    st.header("🧠 Mutlak Analiz")
    if st.button("🚀 ANALİZİ BAŞLAT", use_container_width=True):
        adaylar = []
        for _ in range(200000):
            k = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
            s = engine.skorla(k)
            if s > 0: adaylar.append((k, s))
        
        adaylar.sort(key=lambda x: x[1], reverse=True)
        final = []
        for k, s in adaylar:
            if len(final) >= 10: break
            if not any(len(set(k) & set(f[0])) > 1 for f in final): final.append((k, s))

        for i, (k, s) in enumerate(final, 1):
            ekstra = ""
            if secim == "Çılgın Sayısal": ekstra = f" | ⭐ SS: {random.randint(1, 90)}"
            elif secim == "Şans Topu": ekstra = f" | ➕ Artı: {random.randint(1, 14)}"
            st.success(f"**Tahmin {i}:** {' - '.join([f'{x:02d}' for x in k])}{ekstra} (Skor: {s})")
