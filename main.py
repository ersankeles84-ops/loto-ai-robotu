import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(page_title="Loto AI Master Pro", layout="wide")
st.title("🎰 Loto AI Master - Profesyonel Analiz Paneli")

# 4 Oyunun Ayarları
oyun_listesi = {
    "Sayısal Loto": {"adet": 6, "tavan": 90},
    "Süper Loto": {"adet": 6, "tavan": 60},
    "On Numara": {"adet": 10, "tavan": 80},
    "Şans Topu": {"adet": 5, "tavan": 34}
}

# Hafıza Başlatma
for oyun in oyun_listesi:
    if f"depo_{oyun}" not in st.session_state: st.session_state[f"depo_{oyun}"] = ""
    if f"reset_{oyun}" not in st.session_state: st.session_state[f"reset_{oyun}"] = 0

tabs = st.tabs([f"🔵 {o}" if i==0 else f"🔴 {o}" if i==1 else f"🟢 {o}" if i==2 else f"🟡 {o}" for i, o in enumerate(oyun_listesi)])

def veri_ayikla(metin, tavan):
    if not metin: return []
    # Sadece 1-tavan arası loto sayılarını bulur, tarihleri eler
    bulunanlar = re.findall(r'\b(?:[1-9]|[1-8][0-9]|90)\b', metin)
    return [int(s) for s in bulunanlar if int(s) <= tavan]

def oyun_paneli(oyun, adet, tavan, sekme):
    with sekme:
        st.header(f"{oyun} Merkezi")
        
        # ÜST KISIM: YÜKLEME VE İNDİRME (Yanyana)
        col_dosya1, col_dosya2 = st.columns(2)
        with col_dosya1:
            yukle = st.file_uploader(f"{oyun} Yedek Dosyası Seç", type=["txt"], key=f"file_{oyun}")
            if yukle:
                st.session_state[f"depo_{oyun}"] = yukle.read().decode("utf-8")
                st.success("✅ Veriler yüklendi!")

        with col_dosya2:
            st.write("📂 Hafıza Yönetimi")
            # Buton her zaman görünür, içi boş olsa bile hata vermez
            st.download_button(
                label=f"📥 {oyun} Hafızasını İndir/Yedekle",
                data=st.session_state[f"depo_{oyun}"],
                file_name=f"{oyun.replace(' ', '_')}_yedek.txt",
                mime="text/plain",
                key=f"dl_btn_{oyun}"
            )

        st.divider()

        # ORTA KISIM: VERİ GİRİŞİ
        c1, c2 = st.columns(2)
        with c1:
            # Kutuyu boşaltan anahtar sistemi
            giriş = st.text_area("Yeni Sonuçları Buraya Ekle", height=100, 
                                 key=f"in_{oyun}_{st.session_state[f'reset_{oyun}']}")
            if st.button(f"💾 Hafızaya Kat ve Temizle", key=f"save_{oyun}"):
                if giriş:
                    st.session_state[f"depo_{oyun}"] += "\n" + giriş
                    st.session_state[f"reset_{oyun}"] += 1
                    st.rerun()

        with c2:
            net_datalar = veri_ayikla(st.session_state[f"depo_{oyun}"], tavan)
            st.info(f"🧠 Hafızadaki Toplam Sayı: {len(net_datalar)}")
            if st.button(f"🗑️ Tüm {oyun} Geçmişini Sil", key=f"clear_{oyun}"):
                st.session_state[f"depo_{oyun}"] = ""
                st.rerun()

        # ALT KISIM: TAHMİN
        st.divider()
        if st.button(f"🚀 {oyun} İçin 10 Kolon Üret (6+1)", key=f"predict_{oyun}"):
            if len(net_datalar) < adet:
                st.error("Lütfen önce veri yükleyin!")
            else:
                st.success("🤖 AI Profesyonel Tahminleri:")
                farkli_sayilar = pd.Series(net_datalar).value_counts()
                populer = farkli_sayilar.index.tolist()
                for i in range(1, 11):
                    # Hibrit: Çok çıkanlardan ağırlıklı seçim
                    havuz = populer[:15] * 3 + list(range(1, tavan + 1))
                    ana = sorted(np.random.choice(havuz, adet, replace=False))
                    ss = np.random.randint(1, tavan + 1)
                    st.markdown(f"**Kolon {i}:** `{ana}` | ⭐ **SüperStar:** `{ss}`")

# 4 Oyun için Panelleri Oluştur
for i, (ad, ayar) in enumerate(oyun_listesi.items()):
    oyun_paneli(ad, ayar["adet"], ayar["tavan"], tabs[i])
