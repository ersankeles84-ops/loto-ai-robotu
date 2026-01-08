import streamlit as st
import requests
import base64
import re
import random
from collections import Counter

# Bulut Ayarları
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json()['sha'] if r.status_code == 200 else None
    content = base64.b64encode(metin.encode()).decode()
    data = {"message": "Analiz Guncellendi", "content": content}
    if sha: data["sha"] = sha
    requests.put(url, json=data, headers=headers)

def veri_getir(oyun_adi):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    return base64.b64decode(r.json()['content']).decode() if r.status_code == 200 else ""

st.set_page_config(page_title="Loto AI Data Engine", layout="wide")
st.title("🚀 Loto AI Master - 10.000 Kombinasyon Analiz Motoru")

tab_isimleri = ["Çılgın Sayısal", "Süper Loto", "On Numara", "Şans Topu"]
oyun_ayarlar = {
    "Çılgın Sayısal": {"dosya": "CilginSayisal", "max": 90, "adet": 6, "ek": "Süper Star", "ek_max": 90},
    "Süper Loto": {"dosya": "SuperLoto", "max": 60, "adet": 6, "ek": None, "ek_max": 0},
    "On Numara": {"dosya": "OnNumara", "max": 80, "adet": 22, "ek": None, "ek_max": 0},
    "Şans Topu": {"dosya": "SansTopu", "max": 34, "adet": 5, "ek": "Artı", "ek_max": 14}
}

tabs = st.tabs(tab_isimleri)

for i, tab in enumerate(tabs):
    isim = tab_isimleri[i]
    ayar = oyun_ayarlar[isim]
    
    with tab:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.header("📥 Veri Bankası")
            if f"h_{ayar['dosya']}" not in st.session_state:
                st.session_state[f"h_{ayar['dosya']}"] = veri_getir(ayar['dosya'])
            
            mevcut = st.session_state[f"h_{ayar['dosya']}"]
            tum_sayilar = re.findall(r'\d+', mevcut)
            st.metric("📊 Hafızadaki Toplam Sayı", len(tum_sayilar))
            
            with st.form(key=f"form_{ayar['dosya']}", clear_on_submit=True):
                yeni_veri = st.text_area("Veri Ekle (Tarih ve Sayılar Karışık Olabilir)", height=150)
                if st.form_submit_button("💾 VERİYİ İŞLE VE KAYDET"):
                    st.session_state[f"h_{ayar['dosya']}"] += "\n" + yeni_veri
                    veri_sakla(ayar['dosya'], st.session_state[f"h_{ayar['dosya']}"])
                    st.success("Hafıza Güncellendi!")
                    st.rerun()

        with col2:
            st.header("🔮 Stratejik Tahmin Merkezi")
            if st.button(f"🔥 10.000 KOMBİNASYONU TARA VE EN İYİ 10'U SEÇ", use_container_width=True, key=f"btn_{ayar['dosya']}"):
                if len(tum_sayilar) < 50:
                    st.error("Daha fazla veri lazım kanka!")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # GERÇEK ANALİZ BAŞLIYOR
                    status_text.text("1️⃣ Sayıların çıkma frekansları hesaplanıyor...")
                    frekans = Counter(tum_sayilar)
                    progress_bar.progress(30)
                    
                    status_text.text("2️⃣ 10.000 kombinasyon üretiliyor ve puanlanıyor...")
                    adaylar = []
                    for _ in range(10000):
                        kolon = tuple(sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet'])))
                        # Puanlama: Geçmişte çok çıkan sayıları içeren kolonlar daha yüksek puan alır
                        puan = sum(frekans.get(str(n), 0) for n in kolon)
                        adaylar.append((kolon, puan))
                    progress_bar.progress(70)
                    
                    status_text.text("3️⃣ En yüksek puanlı (en olası) 10 kolon seçiliyor...")
                    adaylar.sort(key=lambda x: x[1], reverse=True)
                    en_iyi_on = adaylar[:10]
                    progress_bar.progress(100)
                    status_text.success("✅ Tarama Tamamlandı! İşte 10.000 ihtimal arasından sıyrılan en güçlü 10 kolon:")

                    
                    
                    for k, (kolon, puan) in enumerate(en_iyi_on, 1):
                        k_str = " - ".join([f"{n:02d}" for n in kolon])
                        if ayar['ek']:
                            ek_no = random.randint(1, ayar['ek_max'])
                            st.markdown(f"**Kolon {k}:** `{k_str}` | 🔥 **{ayar['ek']}: {ek_no:02d}** (Skor: {puan})")
                        else:
                            st.markdown(f"**Kolon {k}:** `{k_str}` (Skor: {puan})")
                    st.balloons()
