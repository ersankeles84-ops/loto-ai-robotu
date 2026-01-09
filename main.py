import streamlit as st
import requests, base64, re, random
from collections import Counter
from datetime import datetime
from itertools import combinations

# --- GITHUB KİMLİK BİLGİLERİ ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_getir(oyun_adi):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return base64.b64decode(r.json()['content']).decode('utf-8')
    except: pass
    return ""

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": "V35 Final Update", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers=headers).status_code in [200, 201]

# --- AKILLI ANALİZ MOTORU ---
class LastStandEngine:
    def __init__(self, raw_data, ayar):
        self.ayar = ayar
        # EVRENSEL TARAYICI: Dosyadaki tüm sayıları format fark etmeksizin çeker
        self.tum_sayilar = [int(n) for n in re.findall(r'\d+', raw_data) if 0 < int(n) <= ayar['max']]
        
        # Sayıları oyunun kolon adedine göre grupla (Analiz için)
        self.cekilisler = [self.tum_sayilar[i:i + ayar['adet']] for i in range(0, len(self.tum_sayilar), ayar['adet'])]
        
        # Birliktelik Matrisi (Geçmişte beraber çıkanlar)
        self.baglar = Counter()
        for c in self.cekilisler:
            if len(c) == ayar['adet']:
                for comb in combinations(sorted(c), 2):
                    self.baglar[comb] += 1
        
        self.frekans = Counter(self.tum_sayilar)

    def analiz_puanla(self, kolon):
        puan = 100.0
        # 1. Grup Dağılımı (Küçük sayı yığılmasını engeller)
        b1 = sum(1 for n in kolon if n <= (self.ayar['max'] // 3))
        b2 = sum(1 for n in kolon if (self.ayar['max'] // 3) < n <= (self.ayar['max'] // 3 * 2))
        b3 = sum(1 for n in kolon if n > (self.ayar['max'] // 3 * 2))
        if b1 > 3 or b2 > 3 or b3 > 3: puan -= 50
        
        # 2. Tek-Çift ve Ardışıklık
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if tekler in [0, self.ayar['adet']]: puan -= 40
        if any(kolon[i+2] - kolon[i] == 2 for i in range(len(kolon)-2)): puan -= 60
        
        # 3. Birliktelik (Geçmiş Veri Gücü)
        for comb in combinations(kolon, 2):
            puan += self.baglar.get(comb, 0) * 5
        return puan

# --- ARAYÜZ ---
st.set_page_config(page_title="Loto AI V35 Last Stand", layout="wide")
st.title("🛡️ Loto AI V35: The Last Stand")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyunlar.keys()))
ayar = oyunlar[secim]

# KRİTİK ADIM: VERİYİ ÇEK
raw_content = veri_getir(ayar['dosya'])
engine = LastStandEngine(raw_content, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("💾 Veri Havuzu")
    # Hafıza Durumu
    if len(engine.tum_sayilar) > 0:
        st.success(f"✅ Hafıza Aktif: {len(engine.tum_sayilar)} sayı okundu.")
        st.info(f"📊 Yaklaşık {len(engine.cekilisler)} çekiliş analiz ediliyor.")
    else:
        st.error("⚠️ Veri Bulunamadı! Lütfen aşağıdan veri ekleyin.")

    with st.form("veri_form", clear_on_submit=True):
        t = st.date_input("Çekiliş Tarihi", datetime.now())
        s = st.text_area("Sonuçlar (Sayıları virgül veya boşlukla girin)")
        if st.form_submit_button("💎 BULUTA MÜHÜRLE"):
            if s.strip():
                yeni_icerik = raw_content + f"\nTarih: {t.strftime('%Y-%m-%d')} | Sonuç: {s}"
                if veri_sakla(ayar['dosya'], yeni_icerik):
                    st.success("Veri kaydedildi, sistem yenileniyor..."); st.rerun()

with col2:
    st.header("🧠 Merkezi Analiz Sistemi")
    if st.button("🚀 MASTER ANALİZİ BAŞLAT", use_container_width=True):
        if len(engine.tum_sayilar) < ayar['adet']:
            st.warning("Analiz yapabilmek için yeterli veri yok!")
        else:
            with st.status("Algoritmalar Çarpıştırılıyor..."):
                adaylar = []
                for _ in range(200000):
                    k = sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet']))
                    p = engine.analiz_puanla(k)
                    if p > 0: adaylar.append((k, p))
                
                adaylar.sort(key=lambda x: x[1], reverse=True)
                final = []
                for k, p in adaylar:
                    if len(final) >= 10: break
                    if not any(len(set(k) & set(f[0])) > 1 for f in final):
                        final.append((k, p))

            for i, (k, p) in enumerate(final, 1):
                ekstra = ""
                if secim == "Çılgın Sayısal": ekstra = f" | ⭐ SS: {random.randint(1, 90)}"
                elif secim == "Şans Topu": ekstra = f" | ➕ Artı: {random.randint(1, 14)}"
                st.info(f"**Tahmin {i}:** {' - '.join([f'{x:02d}' for x in k])}{ekstra} (Skor: {p:.1f})")

st.divider()
st.caption("V35: Evrensel veri ayıklama ve grup dağılım dengesi aktif.")
