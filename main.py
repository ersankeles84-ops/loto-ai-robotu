import streamlit as st
import requests, base64, re, random
from collections import Counter
from itertools import combinations

# --- GITHUB VE GÜVENLİK AYARLARI ---
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    sha = r.json().get('sha') if r.status_code == 200 else None
    data = {"message": f"V19 Update: {oyun}", "content": base64.b64encode(metin.encode()).decode()}
    if sha: data["sha"] = sha
    return requests.put(url, json=data, headers={"Authorization": f"token {TOKEN}"}).status_code in [200, 201]

def veri_getir(oyun):
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{oyun}.txt", headers={"Authorization": f"token {TOKEN}"})
    return base64.b64decode(r.json()['content']).decode() if r.status_code == 200 else ""

# --- ANALİZ MOTORU ---
class OmniEngine:
    def __init__(self, veriler, ayar):
        self.sayilar = [int(n) for n in re.findall(r'\d+', veriler)]
        self.ayar = ayar
        self.frekans = Counter(self.sayilar)
        
    def simulate_monte_carlo(self, kolon, iterations=5000):
        target = 3 if self.ayar['adet'] < 10 else 6
        hits = sum(1 for _ in range(iterations) if len(set(kolon) & set(random.sample(range(1, self.ayar['max']+1), self.ayar['adet']))) >= target)
        return hits / iterations

    def analiz_et(self, kolon):
        score = 100
        if any(kolon[i+1] - kolon[i] == 1 for i in range(len(kolon)-1)): score -= 40 # Ardışıklık cezası
        tekler = sum(1 for n in kolon if n % 2 != 0)
        if not (1 < tekler < self.ayar['adet'] - 1): score -= 30 # Tek-çift dengesi
        return score

# --- ANA ARAYÜZ ---
st.set_page_config(page_title="Loto AI V19 Master", layout="wide")
st.title("🌌 Loto AI V19 Master - Otomatik Temizleme")

oyunlar = {
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6},
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 10},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5}
}

secim = st.sidebar.selectbox("🎯 OYUN SEÇİN", list(oyunlar.keys()))
ayar = oyunlar[secim]

# Veri Akışı
raw_data = veri_getir(ayar['dosya'])
engine = OmniEngine(raw_data, ayar)

col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 Veri Giriş Merkezi")
    st.metric(f"{secim} Hafızası", f"{len(engine.sayilar)} Sayı")
    
    # --- İŞTE O TEMİZLEME ÖZELLİĞİ BURADA ---
    # clear_on_submit=True sayesinde butona basınca kutu boşalır
    with st.form("veri_giris_formu", clear_on_submit=True):
        girdi = st.text_area("Yeni Çekilişleri Buraya Yapıştır", height=200, help="Veriyi gönderdikten sonra burası otomatik temizlenecektir.")
        ekle_butonu = st.form_submit_button("💎 BULUTA MÜHÜRLE", use_container_width=True)
        
        if ekle_butonu:
            if girdi.strip():
                yeni_metin = raw_data + "\n" + girdi
                if veri_sakla(ayar['dosya'], yeni_metin):
                    st.success("Hafıza mühürlendi ve ekran temizlendi!")
                    st.rerun() # Sayfayı yenileyerek yeni hafızayı gösterir
            else:
                st.warning("Kutu boş, mühürlenecek veri yok.")

    # Hafıza Sıfırlama (İhtiyaç olursa diye aşağıda küçük bir buton)
    with st.expander("⚠️ Tehlikeli Bölge"):
        if st.button(f"{secim} Hafızasını Tamamen Sil", type="primary"):
            if veri_sakla(ayar['dosya'], ""): st.rerun()

with col2:
    st.header("🧬 Akıllı Tahmin Çıktısı")
    if st.button("🚀 MASTER ANALİZİ BAŞLAT", use_container_width=True):
        if len(engine.sayilar) < 10: st.warning("Hafıza boş, önce veri yükle kanka!")
        else:
            with st.status("Monte Carlo İşleniyor..."):
                final_sets = []
                while len(final_sets) < 10:
                    kolon = sorted(random.sample(range(1, ayar['max']+1), ayar['adet']))
                    p_score = engine.analiz_et(kolon)
                    if p_score < 60: continue
                    if not any(len(set(kolon) & set(f['k'])) > 2 for f in final_sets):
                        final_sets.append({"k": kolon, "score": p_score, "mc": engine.simulate_monte_carlo(kolon)})

            for i, res in enumerate(final_sets, 1):
                st.success(f"**Kolon {i}:** {' - '.join([f'{x:02d}' for x in res['k']])} | Güç: %{res['score']}")

st.divider()
st.caption("Robot V19: Veri gönderildikten sonra metin alanı otomatik olarak temizlenir.")
