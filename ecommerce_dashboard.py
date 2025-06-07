import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="E-Commerce Dashboard",
    layout="wide"
)

# Inject CSS untuk style sidebar dan tag multiselect
st.markdown("""
<style>
[data-testid="stSidebar"] > div:first-child {
    background-color: #f6f3fa;
    padding: 20px;
    border-right: 1px solid #dedede;
}

.sidebar-title {
    font-size: 22px;
    font-weight: bold;
    color: #6a0dad;
    margin-bottom: 20px;
}

div[data-baseweb="select"] {
    font-family: 'Segoe UI', sans-serif;
}

div[data-baseweb="tag"] {
    background-color: #e5d5f7 !important;
    color: #4a0072 !important;
    font-weight: 600;
    border-radius: 10px;
    padding: 2px 6px;
    border: none !important;
}

div[data-baseweb="tag"]:hover {
    background-color: #d3c0f0 !important;
}

div[data-baseweb="tag"] span {
    color: #4a0072 !important;
    font-weight: 600;
}

div[data-baseweb="tag"] svg {
    color: #6a0dad !important;
}
</style>
""", unsafe_allow_html=True)

import pandas as pd
import plotly.express as px

# Fungsi load data
@st.cache_data
def load_data():
    df = pd.read_csv("E-commerce Website Logs.csv")
    df['accessed_date'] = pd.to_datetime(df['accessed_date'], errors='coerce')
    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    df['sales'] = pd.to_numeric(df['sales'], errors='coerce')
    df['duration_(secs)'] = pd.to_numeric(df['duration_(secs)'], errors='coerce')
    return df.dropna(subset=["accessed_date", "sales", "duration_(secs)"])

df = load_data()

# Sidebar filter
st.sidebar.markdown('<div class="sidebar-title">Filter Data</div>', unsafe_allow_html=True)
gender = st.sidebar.multiselect("Pilih Gender", df['gender'].unique(), default=list(df['gender'].unique()))
membership = st.sidebar.multiselect("Pilih Membership", df['membership'].unique(), default=list(df['membership'].unique()))
pay_method = st.sidebar.multiselect("Pilih Metode Pembayaran", df['pay_method'].unique(), default=list(df['pay_method'].unique()))

filtered_df = df[
    (df['gender'].isin(gender)) &
    (df['membership'].isin(membership)) &
    (df['pay_method'].isin(pay_method))
]

# Judul halaman
st.title("E-Commerce Interactive Dashboard")

st.markdown("""
## Pengantar

Dashboard ini dibuat untuk mengeksplorasi perilaku pengguna dalam platform e-commerce berdasarkan data log interaksi.  
Beberapa aspek penting yang dikaji meliputi:
- Performa penjualan berdasarkan metode pembayaran
- Durasi akses dan hubungannya dengan nilai transaksi
- Tren penjualan harian
- Distribusi berdasarkan negara dan jenis keanggotaan

Pengguna dapat menyesuaikan filter berdasarkan gender, membership, dan metode pembayaran untuk mendapatkan analisis yang lebih spesifik.
""")

# KPI
st.markdown("## Ringkasan Utama")
col1, col2, col3 = st.columns(3)
col1.metric("Total Transaksi", f"{len(filtered_df):,}")
col2.metric("Total Penjualan", f"${filtered_df['sales'].sum():,.2f}")
col3.metric("Durasi Rata-rata", f"{filtered_df['duration_(secs)'].mean():.1f} detik")

# Grafik 1 - Bar Chart Penjualan per Metode Pembayaran
st.markdown("## Penjualan berdasarkan Metode Pembayaran")
pay_chart = filtered_df.groupby("pay_method")["sales"].sum().reset_index()
fig1 = px.bar(
    pay_chart,
    x="pay_method",
    y="sales",
    color_discrete_sequence=["#8e44ad"],
    labels={"pay_method": "Metode Pembayaran", "sales": "Total Penjualan"},
    title="Total Penjualan per Metode Pembayaran"
)
st.plotly_chart(fig1, use_container_width=True)

# Grafik 2 - Pie Chart Proporsi Penjualan
st.markdown("## Proporsi Penjualan Berdasarkan Metode")
fig_pie = px.pie(
    pay_chart,
    names='pay_method',
    values='sales',
    title='Distribusi Proporsi Penjualan per Metode Pembayaran',
    color_discrete_sequence=px.colors.sequential.Purples
)
st.plotly_chart(fig_pie, use_container_width=True)

# Grafik 3 - Line Chart Tren Penjualan Harian
st.markdown("## Tren Penjualan Harian")
daily_sales = filtered_df.groupby(filtered_df["accessed_date"].dt.date)["sales"].sum().reset_index()
fig2 = px.line(
    daily_sales,
    x="accessed_date",
    y="sales",
    labels={"accessed_date": "Tanggal", "sales": "Penjualan"},
    title="Perkembangan Penjualan Harian",
    color_discrete_sequence=["#7f8c8d"]
)
fig2.update_traces(mode="lines+markers")
st.plotly_chart(fig2, use_container_width=True)

# Grafik 4 - Rata-rata Penjualan Berdasarkan Durasi Akses
st.markdown("## Rata-rata Penjualan Berdasarkan Durasi Akses")

# Buat interval durasi
filtered_df["durasi_interval"] = pd.cut(filtered_df["duration_(secs)"], bins=20)

# Hitung rata-rata penjualan per interval
avg_sales = filtered_df.groupby("durasi_interval")["sales"].mean().reset_index()
avg_sales["durasi_str"] = avg_sales["durasi_interval"].astype(str)

fig3 = px.line(
    avg_sales,
    x="durasi_str",
    y="sales",
    markers=True,
    title="Rata-rata Penjualan per Interval Durasi Akses",
    labels={"durasi_str": "Interval Durasi (detik)", "sales": "Rata-rata Penjualan"},
    color_discrete_sequence=["#8e44ad"]
)
st.plotly_chart(fig3, use_container_width=True)

# Grafik 5 - Bar Chart per Membership
st.markdown("## Penjualan berdasarkan Membership")
membership_chart = filtered_df.groupby("membership")["sales"].sum().reset_index()
fig4 = px.bar(
    membership_chart,
    x="membership",
    y="sales",
    color="membership",
    color_discrete_sequence=["#9b59b6", "#bdc3c7", "#8e44ad"],
    labels={"membership": "Membership", "sales": "Total Penjualan"},
    title="Total Penjualan per Tipe Membership"
)
st.plotly_chart(fig4, use_container_width=True)

# Grafik 6 - Country dengan Akses Terbanyak
st.markdown("## Negara dengan Akses Terbanyak")
access_by_country = filtered_df['country'].value_counts().reset_index()
access_by_country.columns = ['country', 'total_access']
fig5 = px.bar(
    access_by_country.head(10),
    x='country',
    y='total_access',
    color_discrete_sequence=["#8e44ad"],
    labels={"country": "Negara", "total_access": "Jumlah Akses"},
    title="10 Negara dengan Akses Terbanyak"
)
st.plotly_chart(fig5, use_container_width=True)

# Grafik 7 - Country dengan Penjualan Tertinggi
st.markdown("## Negara dengan Penjualan Tertinggi")
sales_by_country = filtered_df.groupby("country")["sales"].sum().sort_values(ascending=False).reset_index()
fig6 = px.bar(
    sales_by_country.head(10),
    x="country",
    y="sales",
    color_discrete_sequence=["#7f8c8d"],
    labels={"country": "Negara", "sales": "Total Penjualan"},
    title="10 Negara dengan Nilai Penjualan Tertinggi"
)
st.plotly_chart(fig6, use_container_width=True)

# Kesimpulan
st.markdown("""
---

## Kesimpulan

Berdasarkan eksplorasi data:

1. Metode pembayaran seperti Credit Card dan Debit Card menjadi penyumbang terbesar dalam total penjualan.
2. Durasi sesi yang lebih panjang berkorelasi dengan nilai transaksi yang lebih tinggi.
3. Beberapa negara, seperti yang termasuk dalam 10 besar berdasarkan akses maupun penjualan, menunjukkan potensi strategis yang tinggi untuk promosi dan ekspansi.
4. Segmentasi berdasarkan gender dan tipe keanggotaan memberikan pemahaman lebih lanjut terhadap perilaku pelanggan.
5. Visualisasi pie chart dan line chart membantu menggambarkan distribusi dan tren dengan lebih intuitif.

Dashboard ini dapat digunakan sebagai alat bantu untuk pengambilan keputusan yang berbasis data dalam manajemen e-commerce.

---
""")
