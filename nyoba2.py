import os
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

_ = st.title("Bebras Dashboard")

_ = st.header("Correlation")
cwd = os.getcwd()

chosen_year: str = st.selectbox(
    "Choose the year",
    next(os.walk(os.path.join(cwd, "data")))[1]
)

chosen_category: str = st.selectbox(
    "Choose the category",
    next(os.walk(os.path.join(cwd, "data", chosen_year)))[1]
)

chosen_language: str = st.selectbox(
    "Choose the language",
    next(os.walk(os.path.join(cwd, "data", chosen_year, chosen_category)))[1]
)

chosen_set: str = st.selectbox(
    "Choose the question set",
    next(os.walk(os.path.join(cwd, "data", chosen_year, chosen_category, chosen_language)))[2]
)

# file_suffix = os.path.join(cwd, "data", chosen_year, chosen_category)
# en_file = os.path.join(file_suffix, "en", chosen_set) + ".csv"
# id_file = os.path.join(file_suffix, "id", chosen_set) + ".csv"
# en_df = pd.read_csv(en_file)
# id_df = pd.read_csv(id_file)
# df = pd.concat([en_df, id_df], ignore_index=True)
df: pd.DataFrame = pd.read_csv(os.path.join(cwd, "data", chosen_year, chosen_category, chosen_language, chosen_set))

correlation_df = df.iloc[:, 6:].replace("-", "0").apply(pd.to_numeric, errors='coerce').corr(method="pearson")

fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(correlation_df, annot=True, cmap='coolwarm', center=0, ax=ax);
ax.set_title("Pearson Correlation Heatmap")
st.pyplot(fig)
#boxplot
st.divider()
st.cache_data
def load_and_prepare_data(file_path):
    """Memuat data dari file CSV dan melakukan pembersihan awal."""
    df = pd.read_csv(file_path)
    
    # Ubah 'Time taken' ke detik untuk analisis numerik
    def time_to_seconds(time_str):
        parts = str(time_str).replace('mins', 'min').replace('secs', 'sec').split()
        seconds = 0
        for i, part in enumerate(parts):
            if 'min' in part and i > 0:
                try:
                    seconds += int(parts[i-1]) * 60
                except ValueError:
                    pass # Abaikan jika tidak bisa diubah ke int
            elif 'sec' in part and i > 0:
                try:
                    seconds += int(parts[i-1])
                except ValueError:
                    pass # Abaikan jika tidak bisa diubah ke int
        return seconds if seconds > 0 else 0
    
    df['Time taken (seconds)'] = df['Time taken'].apply(time_to_seconds)
    df['Grade/100.00'] = pd.to_numeric(df['Grade/100.00'], errors='coerce').fillna(0)
    df['School_ID'] = df['Email address'].astype(str)
    
    # PERBAIKAN: Tambahkan loop pembersihan untuk semua kolom soal
    question_cols = [col for col in df.columns if str(col).startswith('Q. ')]
    for col in question_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df

# --- UI Sidebar untuk Filter ---
cwd = os.getcwd()
st.sidebar.header("Filter Utama")

try:
    available_years = next(os.walk(os.path.join(cwd, "data")))[1]
    chosen_year = st.sidebar.selectbox("Pilih Tahun", available_years)

    available_categories = next(os.walk(os.path.join(cwd, "data", chosen_year)))[1]
    chosen_category = st.sidebar.selectbox("Pilih Kategori", available_categories)
except (StopIteration, FileNotFoundError):
    st.error("Struktur folder 'data' tidak ditemukan atau tidak lengkap. Pastikan strukturnya adalah data/{tahun}/{kategori}/...")
    st.stop()

# --- Membuat Tabs untuk Setiap Jenis Analisis ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Analisis Performa Sekolah", 
    "⏱️ Analisis Waktu vs. Skor",
    "🌐 Analisis per Bahasa",
    "🔗 Korelasi Antar Soal"
])


# --- Konten Tab 1: Analisis Performa Sekolah ---
with tab1:
    st.header(f"Distribusi Skor per ID Kelompok ({chosen_category} - {chosen_year})")
    
    # Gabungkan data dari kedua bahasa untuk analisis sekolah
    try:
        id_path = os.path.join(cwd, "data", chosen_year, chosen_category, 'id', 'challenge.csv')
        en_path = os.path.join(cwd, "data", chosen_year, chosen_category, 'en', 'challenge.csv')
        df_id = load_and_prepare_data(id_path)
        df_en = load_and_prepare_data(en_path)
        df_combined = pd.concat([df_id, df_en], ignore_index=True)
    except FileNotFoundError:
        st.warning(f"Data 'challenge.csv' untuk 'id' atau 'en' tidak ditemukan di folder {chosen_category}.")
        st.stop()

    min_participants = st.slider('Tampilkan kelompok dengan minimal peserta:', 1, 50, 5, key='slider_sekolah')
    school_counts = df_combined['School_ID'].value_counts()
    schools_to_show = school_counts[school_counts >= min_participants].index
    df_filtered = df_combined[df_combined['School_ID'].isin(schools_to_show)]

    if not df_filtered.empty:
        fig_box, ax_box = plt.subplots(figsize=(16, 10))
        sns.boxplot(x='School_ID', y='Grade/100.00', data=df_filtered, ax=ax_box)
        ax_box.set_title(f'Distribusi Skor untuk {chosen_category} - {chosen_year}', fontsize=16)
        ax_box.set_xlabel('School / Group ID', fontsize=12)
        ax_box.set_ylabel('Skor Akhir (Grade/100.00)', fontsize=12)
        plt.xticks(rotation=90)
        st.pyplot(fig_box)
    else:
        st.warning(f"Tidak ada kelompok dengan minimal {min_participants} peserta untuk ditampilkan.")

# --- Konten Tab 2: Analisis Waktu vs Skor ---
with tab2:
    st.header("Analisis Waktu Pengerjaan vs. Skor Akhir")
    st.info("Gunakan plot ini untuk mendeteksi anomali. Kelompok di pojok kiri atas (skor tinggi, waktu singkat) sangat mencurigakan.")
    
    fig_scatter, ax_scatter = plt.subplots(figsize=(12, 8))
    sns.scatterplot(data=df_combined, x='Time taken (seconds)', y='Grade/100.00', alpha=0.5, ax=ax_scatter)
    ax_scatter.set_title('Waktu Pengerjaan vs. Skor Akhir')
    ax_scatter.set_xlabel('Waktu Pengerjaan (detik)')
    ax_scatter.set_ylabel('Skor Akhir (Grade/100.00)')
    st.pyplot(fig_scatter)

# --- Konten Tab 3: Analisis per Bahasa ---
with tab3:
    st.header("Perbandingan Kesulitan Soal Antara Bahasa Indonesia dan Inggris")
    
    # Ambil kolom soal
    question_cols = [col for col in df_id.columns if str(col).startswith('Q. ')]
    
    # Hitung rata-rata per soal untuk setiap bahasa
    avg_id = df_id[question_cols].mean().reset_index().rename(columns={0: 'Avg Score', 'index': 'Question'})
    avg_id['Language'] = 'Indonesia'
    
    avg_en = df_en[question_cols].mean().reset_index().rename(columns={0: 'Avg Score', 'index': 'Question'})
    avg_en['Language'] = 'English'
    
    avg_combined = pd.concat([avg_id, avg_en])
    
    fig_lang, ax_lang = plt.subplots(figsize=(16, 8))
    sns.barplot(data=avg_combined, x='Question', y='Avg Score', hue='Language', ax=ax_lang)
    ax_lang.set_title('Rata-rata Skor per Soal Berdasarkan Bahasa')
    ax_lang.set_xlabel('Nomor Soal')
    ax_lang.set_ylabel('Rata-rata Skor')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig_lang)

# --- Konten Tab 4: Korelasi Antar Soal ---
with tab4:
    st.header("Heatmap Korelasi Antar Soal")
    
    # Gunakan data gabungan untuk korelasi yang lebih robust
    correlation_df = df_combined[question_cols].corr(method="pearson")
    
    fig_corr, ax_corr = plt.subplots(figsize=(12, 10))
    sns.heatmap(correlation_df, annot=True, cmap='coolwarm', center=0, ax=ax_corr, fmt='.2f')
    ax_corr.set_title("Pearson Correlation Heatmap")
    st.pyplot(fig_corr)
