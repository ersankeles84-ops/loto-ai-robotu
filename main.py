import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(page_title="Loto AI Master Pro", layout="wide")
st.title("🎰 Loto AI Master - Akıllı ve Kalıcı Analiz")

# Oyun Ayarları
oyunlar = {
    "Sayısal Loto": {"adet": 6, "tavan": 90},
    "Süper Loto": {"adet": 6, "tavan": 60},
    "On Numara": {"adet": 10, "tavan": 80},
    "Şans Topu": {"adet": 5, "tavan": 34}
}

# Hafıza ve Resetleme Başlatma
for oyun in oyunlar:
    if f"depo_{oyun}" not in st.session_state: st.session_state[f"depo_{oyun}"] = ""
    if f"reset_{oyun}" not in st.session_state: st.session_state[f"reset_{oyun}"] = 0

tabs = st.tabs([f"🔵 {o}" if i==0 else f"🔴 {o}" if i==1 else f"🟢 {o}" if i==2 else f"🟡 {o}" for i, o in enumerate(oyunlar)])

def veri_ayikla(metin, tavan):
    if not metin: return []
    # Sadece 1-tavan arası loto sayılarını bulur
    bulunanlar = re.findall(r'\b(?:[1-9]|[1-8][0-9]|90)\b', metin)
    return [int(s) for s in bulunanlar if int(s) <= tavan]

def oyun_paneli(oyun, adet, tavan, sekme):
    with sekme:
        st.subheader(f"📊 {oyun} Merkezi")
        
        # 1. BÖLÜM: VERİ YÜKLEME VE YEDEKLEME
        col_y1, col_y2 = st.columns(2)
        with col_y1:
            yuklenen = st.file_uploader(f"Hafıza Yedek Dosyasını Yükle (.txt)", type=["txt"], key=f"up_{oyun}")
            if yuklenen:
                st.session_state[f"depo_{oyun}"] = yuklenen.read().decode("utf-8")
                st.success("✅ Yedek başarıyla yüklendi!")

        with col_y2:
            if st.session_state[f"depo_{oyun}"]:
                st.download_button(f"📥 {oyun} Hafızasını Telefona Yedekle", 
                                   st.session_state[f"depo_{oyun}"], 
                                   file_name=f"{oyun}_yedek.txt", key=f"dl_{oyun}")

        st.divider()

        # 2. BÖLÜM: YENİ VERİ GİRİŞİ (MANUEL/OTOMATİK)
        c1, c2 = st.columns(2)
        with c1:
            anahtar = f"in_{oyun}_{st.session_state[f'reset_{oyun}']}"
            giriş = st.text_area("Yeni Çekiliş Sonuçlarını Ekle", height=100, key=anahtar)
            
            if st.button(f"💾 Hafızaya Kat ve Temizle", key=f"sv_{oyun}"):
                if giriş:
                    st.session_state[f"depo_{oyun}"] += "\n" + giriş
                    st.session_state[f"reset_{oyun}"] += 1
                    st.success("✅ Hafızaya eklendi!")
                    st.rerun()

        with c2:
            net_sayilar = veri_ayikla(st.session_state[f"depo_{oyun}"], tavan)
            st.info(f"🧠 Hafıza Durumu: {len(net_sayilar)} Sayı")
            if st.button(f"🗑️ Tüm Hafızayı SIFIRLA", key=f"clr_{oyun}"):
                st.session_state[f"depo_{oyun}"] = ""
                st.rerun()

        st.divider()

        # 3. BÖLÜM: TAHMİN ÜRETME
        if st.button(f"🚀 10 Kolon Tahmini Üret (6+1)", key=f"pre_{oyun}"):
            if len(net_sayilar) < adet * 2:
                st.error("Daha fazla veri yüklemelisiniz!")
            else:
                st.success("🤖 AI Profesyonel Tahminleri:")
                farkli_sayilar = pd.Series(net_sayilar).value_counts()
                populer = farkli_sayilar.index.tolist()
                for i in range(1, 11):
                    # Hibrit Seçim: Çok çıkanlar %70, Şans %30
                    havuz = populer[:15] * 4 + list(range(1, tavan + 1))
                    ana = sorted(np.random.choice(havuz, adet, replace=False))
                    ss = np.random.randint(1, tavan + 1)
                    st.markdown(f"**Kolon {i}:** `{ana}` | ⭐ **SüperStar:** `{ss}`")

# Robotu Çalıştır
for i, (oyun, ayar) in enumerate(oyunlar.items()):
    oyun_paneli(oyun, ayar["adet"], ayar["tavan"], tabs[i])
