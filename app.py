# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
from pathlib import Path

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Promo & Margin Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MUAT DATA ---
@st.cache_data
def load_data():
    # Menggunakan low_memory=False untuk menghindari warning tipe data campuran
    df = pd.read_csv("data/processed/unified_data_with_metrics.csv", parse_dates=['order_date'], low_memory=False)
    return df

df = load_data()

# --- SIDEBAR FILTER ---
st.sidebar.header("⚙️ Filter Dashboard")
source_filter = st.sidebar.multiselect(
    "Pilih Sumber Data:",
    options=df['data_source'].unique(),
    default=df['data_source'].unique()
)

# Filter dataframe berdasarkan pilihan
df_filtered = df[df['data_source'].isin(source_filter)].copy()

# --- HEADER UTAMA ---
st.title("📊 Promo & Margin Intelligence Dashboard")
st.markdown("Analisis deteksi **Kanibalisasi Promosi** dan **Kebocoran Margin (Revenue Leakage)** untuk optimasi profitabilitas.")
st.markdown("---")

# --- TAB NAVIGASI ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Ringkasan Eksekutif", "🚨 Audit Kebocoran (Leakage)", "🔄 Analisis Kanibalisasi", "💡 Rekomendasi Bisnis", " Prediksi ML"])

# ==========================================
# TAB 1: RINGKASAN EKSEKUTIF
# ==========================================
with tab1:
    st.subheader("KPI Utama (Berdasarkan Filter)")
    
    # Hitung metrik agregat
    total_revenue = df_filtered['revenue'].sum()
    total_profit = df_filtered['absolute_profit'].sum()
    total_leakage_loss = df_filtered[df_filtered['is_leakage'] == True]['absolute_profit'].sum()
    leakage_tx_count = len(df_filtered[df_filtered['is_leakage'] == True])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"Rp {total_revenue:,.0f}")
    col2.metric("Total Profit", f"Rp {total_profit:,.0f}", delta=f"{(total_profit/total_revenue*100):.1f}%" if total_revenue > 0 else "0%")
    col3.metric("Transaksi Bocor", f"{leakage_tx_count:,}", delta_color="inverse")
    col4.metric("Est. Kerugian Profit", f"Rp {total_leakage_loss:,.0f}", delta_color="inverse")

    # Tren Revenue & Profit per Bulan
    st.markdown("#### Tren Pendapatan & Profitabilitas per Bulan")
    monthly_trend = df_filtered.groupby(df_filtered['order_date'].dt.to_period('M').astype(str)).agg(
        revenue=('revenue', 'sum'),
        profit=('absolute_profit', 'sum')
    ).reset_index()
    monthly_trend.rename(columns={'order_date': 'Bulan'}, inplace=True)

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(x=monthly_trend['Bulan'], y=monthly_trend['revenue'], name='Revenue', marker_color='royalblue'))
    fig_trend.add_trace(go.Scatter(x=monthly_trend['Bulan'], y=monthly_trend['profit'], name='Profit', marker_color='green', mode='lines+markers'))
    fig_trend.update_layout(barmode='overlay', xaxis_title='Bulan', yaxis_title='Nilai (Rp)', hovermode='x unified')
    st.plotly_chart(fig_trend, use_container_width=True)

# ==========================================
# TAB 2: AUDIT KEBOCORAN (LEAKAGE)
# ==========================================
with tab2:
    st.subheader("🚨 The Discount Trap: Di Mana Uang Terbakar?")
    st.info("Visualisasi ini menunjukkan hubungan langsung antara tingkat diskon dan profitabilitas. Area merah menunjukkan kerugian.")

    # 1. Profit berdasarkan Band Diskon
    df_filtered['discount_band'] = pd.cut(df_filtered['discount_rate'], [0, 0.001, 0.2, 0.4, 0.8], labels=['0%', '1-20%', '21-40%', '41-80%'])
    band_profit = df_filtered.groupby('discount_band', observed=True)['absolute_profit'].sum().reset_index()
    
    fig_band = px.bar(band_profit, x='discount_band', y='absolute_profit', 
                      color='absolute_profit', color_continuous_scale='RdYlGn',
                      labels={'discount_band': 'Tingkat Diskon', 'absolute_profit': 'Total Profit'},
                      title="Total Profit Berdasarkan Tingkat Diskon")
    st.plotly_chart(fig_band, use_container_width=True)

    # 2. Scatter Plot: Diskon vs Profit per Transaksi (Sampling agar tidak berat)
    st.markdown("#### Scatter Plot: Diskon vs Profit per Transaksi (Sampel 2000 data)")
    sample_df = df_filtered.sample(2000, random_state=42)
    fig_scatter = px.scatter(sample_df, x='discount_rate', y='absolute_profit', 
                             color='is_leakage', color_discrete_map={True: 'red', False: 'gray'},
                             opacity=0.6, labels={'discount_rate': 'Discount Rate', 'absolute_profit': 'Profit'},
                             title="Apakah Diskon Tinggi Selalu Menguntungkan? (Titik Merah = Kebocoran)")
    st.plotly_chart(fig_scatter, use_container_width=True)

# ==========================================
# TAB 3: ANALISIS KANIBALISASI
# ==========================================
with tab3:
    st.subheader("🔄 Dinamika Antar Kategori Produk")
    st.warning("Catatan: Karena granularitas SKU terbatas, analisis dilakukan di level Kategori untuk mendeteksi pergeseran permintaan.")

    # Performa per Kategori
    cat_perf = df_filtered.groupby('category').agg(
        total_revenue=('revenue', 'sum'),
        total_profit=('absolute_profit', 'sum'),
        avg_discount=('discount_rate', 'mean')
    ).reset_index()
    cat_perf['profit_margin_pct'] = (cat_perf['total_profit'] / cat_perf['total_revenue']) * 100

    col1, col2 = st.columns(2)
    
    with col1:
        fig_cat_rev = px.pie(cat_perf, values='total_revenue', names='category', title="Kontribusi Revenue per Kategori")
        st.plotly_chart(fig_cat_rev, use_container_width=True)
        
    with col2:
        fig_cat_margin = px.bar(cat_perf, x='category', y='profit_margin_pct', color='avg_discount',
                                labels={'profit_margin_pct': 'Margin Profit (%)', 'avg_discount': 'Rata-rata Diskon'},
                                title="Margin Profit vs Rata-rata Diskon per Kategori")
        st.plotly_chart(fig_cat_margin, use_container_width=True)

# ==========================================
# TAB 4: REKOMENDASI BISNIS
# ==========================================
with tab4:
    st.subheader("💡 Rekomendasi Strategis Berdasarkan Data")
    
    st.markdown("""
    Berdasarkan analisis data di atas, berikut adalah rekomendasi aksi untuk tim manajemen:
    
    1. **Hentikan Diskon >40% Secara Default**  
       Data menunjukkan 100% transaksi pada band diskon 41-80% mengalami kerugian (`pct_rugi = 1.0`). Diskon sebesar ini hanya membakar margin tanpa memberikan *incremental lift* yang sepadan.
    
    2. **Ganti Diskon Langsung dengan Strategi Bundling**  
       Untuk kategori dengan margin tipis namun volume tinggi, pertimbangkan bundling dengan produk ber-margin tinggi alih-alih memberikan potongan harga langsung yang menggerus profit.
    
    3. **Segmentasi Pelanggan yang Lebih Ketat**  
       Kebocoran terjadi karena diskon diberikan secara membabi buta. Terapkan mekanisme promo yang hanya aktif untuk *new user* atau *churned user*, bukan untuk pelanggan loyal yang sudah memiliki niat beli tinggi (willingness to pay).
    
    4. **Audit Kategori 'Office Supplies' / 'Home'**  
       *(Sesuaikan dengan kategori yang marginnya tergerus paling parah di dataset)*. Kategori ini menunjukkan rata-rata diskon tinggi namun kontribusinya terhadap profit bersih sangat minim atau bahkan negatif.
    """)
# ==========================================
# TAB 5: PREDIKSI ML
# ==========================================
with tab5:
    st.subheader("🤖 Prediksi Risiko Kebocoran Margin (Real-time)")
    st.markdown("Gunakan model Machine Learning (Random Forest) untuk memprediksi apakah parameter transaksi berikut berisiko menyebabkan kerugian.")
    
    # Load Model
    @st.cache_resource
    def load_model():
        return joblib.load("models/leakage_predictor.pkl"), joblib.load("models/feature_names.pkl")
    
    try:
        model, feature_names = load_model()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            discount_rate = st.slider("Tingkat Diskon (0 - 1.0)", 0.0, 1.0, 0.2, 0.05)
        with col2:
            quantity = st.number_input("Jumlah Qty", 1, 100, 5)
        with col3:
            revenue = st.number_input("Estimasi Revenue (Rp)", 1000, 1000000, 50000, 1000)
            
        category = st.selectbox("Kategori", df['category'].unique())
        data_source = st.selectbox("Sumber Data", df['data_source'].unique())
        
        if st.button("🔮 Prediksi Risiko Kebocoran"):
            # Siapkan data input sesuai format training
            input_data = pd.DataFrame([{
                'discount_rate': discount_rate,
                'quantity': quantity,
                'revenue': revenue,
                'absolute_profit': 0, # Dummy, model akan memprediksi is_leakage
                'category': category,
                'data_source': data_source,
                'region': 'North America' # Dummy region
            }])
            
            # One-hot encoding sesuai training
            input_data = pd.get_dummies(input_data, columns=['category', 'data_source', 'region'], drop_first=True)
            
            # Pastikan semua kolom fitur ada (isi 0 jika tidak ada)
            for col in feature_names:
                if col not in input_data.columns:
                    input_data[col] = 0
                    
            input_data = input_data[feature_names]
            
            # Prediksi
            prediction = model.predict(input_data)[0]
            probability = model.predict_proba(input_data)[0]
            
            if prediction == 1:
                st.error(f"️ **PERINGATAN TINGGI!** Transaksi ini diprediksi mengalami **KEBOCORAN MARGIN**.")
                st.write(f"Keyakinan Model: **{probability[1]*100:.2f}%**")
            else:
                st.success(f"✅ **AMAN.** Transaksi ini diprediksi **MENGUNTUNGKAN**.")
                st.write(f"Keyakinan Model: **{probability[0]*100:.2f}%**")
                
    except FileNotFoundError:
        st.warning("Model belum dilatih. Silakan jalankan `python src/ml_leakage.py` terlebih dahulu.")
# --- FOOTER ---
st.markdown("---")
st.caption("Dibangun untuk Portofolio Analisis Data | Sumber Data: Kaggle (Superstore & E-commerce Synthetic) | © 2026")