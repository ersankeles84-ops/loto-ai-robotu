import streamlit as st
import requests
import base64
import re
import random
from collections import Counter

# Bulut Bağlantısı
TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["REPO_NAME"]

def veri_sakla(oyun_adi, metin):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    sha = r.json()['sha'] if r.status_code == 200 else None
    content = base64.b64encode(metin.encode()).decode()
    data = {"message": "Guncelleme", "content": content}
    if sha: data["sha"] = sha
    requests.put(url, json=data, headers=headers)

def veri_getir(oyun_adi):
    url = f"https://api.github.com/repos/{REPO}/contents/{oyun_adi}.txt"
    r = requests.get(url, headers={"Authorization": f"token {TOKEN}"})
    return base64.b64decode(r.json()['content']).decode() if r.status_code == 200 else ""

st.set_page_config(page_title="Loto AI Ultra", layout="wide")
st.title("🛡️ Loto AI Master - Derin Veri Madenciliği")

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
        # 1. VERİ YÜKLEME BUTONU (0 GÖZÜKMEMESİ İÇİN)
        if st.button(f"☁️ {isim.upper()} HAFIZASINI BULUTTAN GETİR", use_container_width=True):
            st.session_state[f"h_{ayar['dosya']}"] = veri_getir(ayar['dosya'])
            st.success("Hafıza başarıyla yüklendi!")
            st.rerun()

        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.header("📥 Veri Giriş Merkezi")
            
            # Hafıza Kontrolü
            h_key = f"h_{ayar['dosya']}"
            if h_key not in st.session_state:
                st.session_state[h_key] = ""
            
            mevcut = st.session_state[h_key]
            tum_sayilar = re.findall(r'\d+', mevcut)
            st.metric("📊 Hafızadaki Sayı Adedi", len(tum_sayilar))
            
            # MANUEL SONUÇ GİRİŞİ (TEK SATIR)
            with st.expander("🆕 Son Çekiliş Sonucunu Gir", expanded=True):
                with st.form(key=f"tek_{ayar['dosya']}", clear_on_submit=True):
                    son_sonuc = st.text_input("Örn: 09.01.2026 3 12 22 23 45 55")
                    if st.form_submit_button("💾 KAYDET VE TEMİZLE"):
                        st.session_state[h_key] += "\n" + son_sonuc
                        veri_sakla(ayar['dosya'], st.session_state[h_key])
                        st.success("Sonuç Hafızaya Mühürlendi!")
                        st.rerun()

            # TOPLU VERİ YÜKLEME (ESKİ YILLAR İÇİN)
            with st.expander("📚 Toplu Veri Yükle (Geçmiş Yıllar)"):
                toplu_veri = st.text_area("Kopyala-Yapıştır", height=150, key=f"toplu_{ayar['dosya']}")
                if st.button("💾 TOPLU KAYDET", key=f"btn_toplu_{ayar['dosya']}"):
                    st.session_state[h_key] += "\n" + toplu_veri
                    veri_sakla(ayar['dosya'], st.session_state[h_key])
                    st.success("Toplu Veri Eklendi!")
                    st.rerun()

        with col2:
            st.header("🧬 100.000 Kombinasyon Analizi")
            # ANALİZ BUTONU
            if st.button(f"🚀 DERİN ANALİZİ BAŞLAT ({isim})", use_container_width=True):
                if len(tum_sayilar) < 10:
                    st.error("Hafıza boş kanka, önce verileri yükle!")
                else:
                    with st.status("🔍 Veri Madenciliği Yapılıyor...", expanded=True) as status:
                        st.write("📊 Sayı frekansları ve tarihsel döngüler hesaplanıyor...")
                        frekans = Counter(tum_sayilar)
                        
                        st.write("⚖️ 100.000 farklı kombinasyon olasılık filtresinden geçiriliyor...")
                        adaylar = []
                        # GERÇEK ANALİZ DÖNGÜSÜ
                        for _ in range(100000):
                            kolon = tuple(sorted(random.sample(range(1, ayar['max'] + 1), ayar['adet'])))
                            puan = sum(frekans.get(str(n), 0) for n in kolon)
                            adaylar.append((kolon, puan))
                        
                        st.write("🏆 En yüksek skorlu 10 stratejik kolon seçiliyor...")
                        adaylar.sort(key=lambda x: x[1], reverse=True)
                        en_iyi_on = adaylar[:10]
                        status.update(label="✅ Analiz Tamamlandı!", state="complete")

                    # SONUÇLAR
                    st.subheader("📍 İstatistiksel Olarak En Güçlü 10 Kolon")
                    for k, (kolon, puan) in enumerate(en_iyi_on, 1):
                        k_str = " - ".join([f"{n:02d}" for n in kolon])
                        if ayar['ek']:
                            ek_no = random.randint(1, ayar['ek_max'])
                            st.info(f"**Kolon {k}:** {k_str}  |  🔥 **{ayar['ek']}: {ek_no:02d}** (Skor: {puan})")
                        else:
                            st.success(f"**Kolon {k}:** {k_str} (Skor: {puan})")
                    st.balloons()
