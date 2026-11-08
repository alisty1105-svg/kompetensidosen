
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from pathlib import Path

# =====================================================
# 1. KONFIGURASI HALAMAN
# =====================================================

st.set_page_config(
    page_title="Sistem Kompetensi Dosen",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. DESAIN CSS
# =====================================================

st.markdown("""
<style>
    .stApp {
        background-color: #F4F7FB;
    }

    [data-testid="stSidebar"] {
        background-color: #102A43;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    .main-title {
        font-size: 30px;
        font-weight: 800;
        color: #102A43;
        margin-bottom: 3px;
    }

    .subtitle {
        color: #627D98;
        font-size: 14px;
        margin-bottom: 25px;
    }

    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #E5EAF0;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    }

    .metric-label {
        font-size: 13px;
        color: #627D98;
    }

    .metric-value {
        font-size: 27px;
        font-weight: 800;
        color: #102A43;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 10px;
    }

    .footer {
        text-align: center;
        color: #829AB1;
        font-size: 12px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. KONFIGURASI DATASET
# =====================================================

FILE_DEFAULT = "kompetensidosen.xlsx"

SHEETS = {
    "Data Dosen": "01_Identitas_Dosen",
    "Data BKD": "02_Data_BKD",
    "Jabatan Akademik": "03_Jabatan_Akademik",
    "Pembelajaran": "04_Pembelajaran",
    "Penelitian": "05_Penelitian",
    "Pengabdian": "06_Pengabdian",
    "Pengembangan Profesional": "07_Pengembangan_Profesional",
    "Penilaian Kompetensi": "08_Penilaian_Kompetensi",
    "Profil Kompetensi": "09_Profil_Kompetensi",
    "Referensi Indikator": "10_Referensi_Indikator"
}

# =====================================================
# 4. MEMBACA DATA EXCEL
# =====================================================

@st.cache_data
def load_data(file):
    return pd.read_excel(file, sheet_name=None)

st.sidebar.markdown("# 🎓 SIMKOMDOS")
st.sidebar.caption("Sistem Informasi Kompetensi Dosen")
st.sidebar.divider()

uploaded_file = st.sidebar.file_uploader(
    "Unggah Dataset Excel",
    type=["xlsx"]
)

file_source = uploaded_file if uploaded_file else FILE_DEFAULT

if uploaded_file is None and not Path(FILE_DEFAULT).exists():
    st.error(
        "Dataset belum ditemukan. Letakkan file Excel "
        "di folder yang sama dengan app.py atau unggah melalui sidebar."
    )
    st.stop()

try:
    data = load_data(file_source)
except Exception as e:
    st.error(f"Gagal membaca dataset: {e}")
    st.stop()

# =====================================================
# 5. NAVIGASI SIDEBAR
# =====================================================

menu = [
    "Dashboard",
    "Data Dosen",
    "Data BKD",
    "Jabatan Akademik",
    "Pembelajaran",
    "Penelitian",
    "Pengabdian",
    "Pengembangan Profesional",
    "Penilaian Kompetensi",
    "Profil Kompetensi",
    "Referensi Indikator",
    "Ekspor Data"
]

selected_menu = st.sidebar.radio(
    "MENU UTAMA",
    menu,
    index=0
)

st.sidebar.divider()
st.sidebar.caption("SIMKOMDOS | Versi 1.0")
st.sidebar.caption("Pengembangan Dashboard Akademik")


# =====================================================
# 6. FUNGSI PEMANGGIL DATA
# =====================================================

def get_df(menu_name):
    sheet_name = SHEETS[menu_name]
    return data[sheet_name].copy()


def title_page(title, description):
    st.markdown(
        f'<div class="main-title">{title}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="subtitle">{description}</div>',
        unsafe_allow_html=True
    )


def show_table(df):
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


def metric_card(label, value, icon):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def filter_data(df):
    result = df.copy()

    if "prodi" in result.columns:
        pilihan = ["Semua"] + sorted(
            result["prodi"].dropna().astype(str).unique().tolist()
        )

        prodi = st.selectbox(
            "Filter Program Studi",
            pilihan
        )

        if prodi != "Semua":
            result = result[
                result["prodi"].astype(str) == prodi
            ]

    if "tahun" in result.columns:
        tahun_list = sorted(
            result["tahun"].dropna().unique().tolist()
        )

        if tahun_list:
            tahun = st.selectbox(
                "Filter Tahun",
                ["Semua"] + tahun_list
            )

            if tahun != "Semua":
                result = result[result["tahun"] == tahun]

    return result


# =====================================================
# 7. HALAMAN DASHBOARD
# =====================================================

if selected_menu == "Dashboard":

    title_page(
        "Dashboard Kompetensi Dosen",
        "Ringkasan data dan analisis kompetensi dosen"
    )

    dosen = get_df("Data Dosen")
    bkd = get_df("Data BKD")
    profil = get_df("Profil Kompetensi")

    # Kartu statistik
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Total Dosen",
            f"{dosen['id_dosen'].nunique():,}",
            "👨‍🏫"
        )

    with c2:
        if "status_aktif" in dosen.columns:
            aktif = dosen["status_aktif"].astype(str).str.lower().isin(
                ["true", "1", "ya", "aktif"]
            ).sum()
        else:
            aktif = 0

        metric_card("Dosen Aktif", f"{aktif:,}", "🟢")

    with c3:
        memenuhi = (
            bkd["status_bkd"].astype(str)
            .str.lower().eq("memenuhi").sum()
            if "status_bkd" in bkd.columns else 0
        )

        metric_card("BKD Memenuhi", f"{memenuhi:,}", "📋")

    with c4:
        metric_card(
            "Profil Kompetensi",
            f"{profil['id_dosen'].nunique():,}",
            "📊"
        )

    st.write("")

    # Grafik jumlah dosen berdasarkan prodi
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribusi Dosen per Program Studi")

        if "prodi" in dosen.columns:
            prodi_data = (
                dosen["prodi"]
                .value_counts()
                .reset_index()
            )

            prodi_data.columns = ["Program Studi", "Jumlah"]

            fig = px.pie(
                prodi_data,
                names="Program Studi",
                values="Jumlah",
                hole=0.55,
                color_discrete_sequence=px.colors.qualitative.Set2
            )

            fig.update_layout(
                height=350,
                margin=dict(t=20, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Komposisi Jabatan Akademik")

        jabatan = get_df("Jabatan Akademik")

        if "jabatan_akademik" in jabatan.columns:
            jab_data = (
                jabatan["jabatan_akademik"]
                .value_counts()
                .reset_index()
            )

            jab_data.columns = ["Jabatan", "Jumlah"]

            fig = px.bar(
                jab_data,
                x="Jabatan",
                y="Jumlah",
                color="Jabatan",
                text="Jumlah"
            )

            fig.update_layout(
                height=350,
                showlegend=False,
                margin=dict(t=20, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)

    # Rata-rata enam dimensi kompetensi
    st.subheader("Rata-rata Kompetensi Dosen")

    dimensi = {
        "Pedagogik": "skor_pedagogik",
        "Profesional": "skor_profesional",
        "Penelitian": "skor_penelitian",
        "Pengabdian": "skor_pengabdian",
        "Digital": "skor_digital",
        "Pengembangan Profesional": "skor_pengembangan_diri"
    }

    available = {
        label: col for label, col in dimensi.items()
        if col in profil.columns
    }

    if available:
        values = [
            pd.to_numeric(profil[col], errors="coerce").mean()
            for col in available.values()
        ]

        chart_data = pd.DataFrame({
            "Dimensi": list(available.keys()),
            "Rata-rata": values
        })

        fig = px.bar(
            chart_data,
            x="Dimensi",
            y="Rata-rata",
            color="Rata-rata",
            text_auto=".2f",
            color_continuous_scale="Blues"
        )

        fig.update_layout(
            height=400,
            yaxis_range=[0, 5]
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Data Profil Kompetensi Terbaru")
    show_table(profil.head(10))


# =====================================================
# 8. HALAMAN DATA UMUM
# =====================================================

elif selected_menu in [
    "Data Dosen",
    "Data BKD",
    "Jabatan Akademik",
    "Pembelajaran",
    "Penelitian",
    "Pengabdian",
    "Pengembangan Profesional",
    "Penilaian Kompetensi",
    "Profil Kompetensi",
    "Referensi Indikator"
]:

    descriptions = {
        "Data Dosen": "Informasi identitas dan karakteristik dosen.",
        "Data BKD": "Informasi beban kerja dosen setiap semester.",
        "Jabatan Akademik": "Riwayat jabatan akademik dosen.",
        "Pembelajaran": "Data aktivitas dan kualitas pembelajaran.",
        "Penelitian": "Data kegiatan penelitian dan publikasi.",
        "Pengabdian": "Data pengabdian kepada masyarakat.",
        "Pengembangan Profesional": "Pelatihan, workshop, dan sertifikasi.",
        "Penilaian Kompetensi": "Penilaian berdasarkan 25 indikator.",
        "Profil Kompetensi": "Rekapitulasi enam dimensi kompetensi.",
        "Referensi Indikator": "Daftar indikator kompetensi dosen."
    }

    title_page(
        selected_menu,
        descriptions[selected_menu]
    )

    df = get_df(selected_menu)

    st.markdown("### Filter dan Pencarian")

    filtered = filter_data(df)

    search = st.text_input(
        "🔎 Cari data",
        placeholder="Masukkan kata kunci..."
    )

    if search:
        mask = filtered.astype(str).apply(
            lambda col: col.str.contains(
                search,
                case=False,
                na=False
            )
        ).any(axis=1)

        filtered = filtered[mask]

    st.caption(f"Jumlah data: {len(filtered)} baris")

    show_table(filtered)

    st.divider()

    st.subheader("Unduh Data")

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        filtered.to_excel(
            writer,
            index=False,
            sheet_name="Data"
        )

    st.download_button(
        "📥 Download Excel",
        data=output.getvalue(),
        file_name=f"{selected_menu.lower().replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =====================================================
# 9. HALAMAN EKSPOR DATA
# =====================================================

elif selected_menu == "Ekspor Data":

    title_page(
        "Ekspor Dataset",
        "Unduh seluruh dataset kompetensi dosen dalam satu workbook."
    )

    st.info(
        "Seluruh sheet pada workbook akan dimasukkan "
        "ke dalam satu file Excel."
    )

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in data.items():
            df.to_excel(
                writer,
                index=False,
                sheet_name=sheet_name[:31]
            )

    st.download_button(
        "📥 Download Seluruh Dataset",
        data=output.getvalue(),
        file_name="dataset_kompetensi_dosen.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# =====================================================
# 10. FOOTER
# =====================================================

st.markdown("""
<div class="footer">
    SISTEM INFORMASI KOMPETENSI DOSEN<br>
    Dashboard Analisis Data Akademik | Python & Streamlit
</div>
""", unsafe_allow_html=True)
