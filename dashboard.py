import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# ==========================================
# 1. PENGATURAN HALAMAN
# ==========================================
st.set_page_config(page_title="Dashboard Sentimen MBG", page_icon="🍽️", layout="wide")

# ==========================================
# 2. KONEKSI REST API SUPABASE
# ==========================================
# MASUKKAN URL DAN KEY SUPABASE MILIKMU DI SINI
SUPABASE_URL = "https://vcngqonjewrskaraczjy.supabase.co"
SUPABASE_KEY = "sb_publishable_HvgsBy9OA6wzdo2O91FSNQ_vHSKRVzD"

# Endpoint untuk mengambil semua data (select=*) dari tabel sentimen_mbg
API_URL = f"{SUPABASE_URL}/rest/v1/sentimen_mbg?select=*"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

# ==========================================
# 3. FUNGSI MENARIK DATA 
# ==========================================
@st.cache_data(ttl=60) 
def ambil_data():
    try:
        # Mengetuk pintu Supabase lewat jalur REST API
        respons = requests.get(API_URL, headers=HEADERS)
        
        if respons.status_code == 200:
            # Ubah data JSON menjadi format tabel Pandas
            return pd.DataFrame(respons.json())
        else:
            st.error(f"Gagal mengambil data. Kode Error: {respons.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Koneksi terputus: {e}")
        return pd.DataFrame()

df = ambil_data()

df = ambil_data()

# ==========================================
# KODE PENYELAMAT: STANDARISASI LABEL
# ==========================================
if not df.empty and 'label_sentimen' in df.columns:
    # 1. Ubah semuanya jadi huruf besar dulu (agar 'positive' jadi 'POSITIVE')
    df['label_sentimen'] = df['label_sentimen'].astype(str).str.upper()
    
    # 2. Jika AI ternyata memakai kode mesin (LABEL_0, dll), kita terjemahkan otomatis
    kamus_label = {
        'LABEL_0': 'NEUTRAL',
        'LABEL_1': 'POSITIVE',
        'LABEL_2': 'NEGATIVE',
        'NEGATIF': 'NEGATIVE', # Jaga-jaga kalau bahasa Indonesia
        'POSITIF': 'POSITIVE'
    }
    df['label_sentimen'] = df['label_sentimen'].replace(kamus_label)
# ==========================================

# ==========================================
# 4. DESAIN ANTARMUKA (UI) DASHBOARD
# ==========================================
st.title("📊 Dashboard Analisis Sentimen Program MBG")
st.markdown("Analisis sentimen masyarakat di X menggunakan **Indo-BERT**.")
st.markdown("---")

if df.empty:
    st.warning("Belum ada data di Supabase atau periksa kembali URL/Key milikmu.")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Cuitan", len(df))
    col2.metric("Positif 😊", len(df[df['label_sentimen'] == 'POSITIVE']))
    col3.metric("Negatif 😠", len(df[df['label_sentimen'] == 'NEGATIVE']))
    col4.metric("Netral 😐", len(df[df['label_sentimen'] == 'NEUTRAL']))
    
    st.markdown("---")
    grafik_col1, grafik_col2 = st.columns(2)
    
    with grafik_col1:
        st.subheader("Distribusi Sentimen")
        fig_pie = px.pie(df, names='label_sentimen', color='label_sentimen',
                         color_discrete_map={'POSITIVE':'#00cc96', 'NEGATIVE':'#ef553b', 'NEUTRAL':'#636efa'}, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    with grafik_col2:
        st.subheader("Sentimen Berdasarkan Aspek")
        df_aspek = df.groupby(['aspek', 'label_sentimen']).size().reset_index(name='jumlah')
        fig_bar = px.bar(df_aspek, x='aspek', y='jumlah', color='label_sentimen', barmode='group',
                         color_discrete_map={'POSITIVE':'#00cc96', 'NEGATIVE':'#ef553b', 'NEUTRAL':'#636efa'})
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("Data Hasil Analisis Terbaru")
    
    # Menggunakan st.table agar super ringan dan stabil
    # Menyesuaikan dengan kolom default jika 'waktu_dibuat' tidak ada
    kolom_penting = ['teks_asli', 'aspek', 'label_sentimen', 'skor_kepercayaan']
    kolom_tersedia = [col for col in kolom_penting if col in df.columns]
    
    df_tabel = df[kolom_tersedia].tail(15)
    st.table(df_tabel)