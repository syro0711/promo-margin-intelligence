# src/metrics.py
import pandas as pd
import numpy as np

def calculate_discount_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghitung metrik dasar terkait diskon, biaya diskon, dan potensi kebocoran.
    """
    df = df.copy()
    
    # 1. Menghitung Gross Revenue (Pendapatan sebelum diskon)
    # Rumus: Revenue = Gross * (1 - discount_rate) -> Gross = Revenue / (1 - discount_rate)
    # Kita hindari pembagian dengan nol jika discount_rate = 1 (100%)
    df['gross_revenue'] = np.where(
        df['discount_rate'] < 1.0, 
        df['revenue'] / (1 - df['discount_rate']), 
        df['revenue']
    )
    
    # 2. Menghitung Discount Cost (Biaya yang dikeluarkan untuk diskon)
    df['discount_cost'] = df['gross_revenue'] - df['revenue']
    
    # 3. Menghitung Profit Margin Percentage (Persentase Margin)
    df['profit_margin_pct'] = np.where(
        df['gross_revenue'] > 0, 
        (df['absolute_profit'] / df['gross_revenue']) * 100, 
        0
    )
    
    # 4. Menandai Kebocoran (Leakage Flag)
    # Skenario kebocoran: Diskon diberikan, tapi profit tetap negatif atau margin sangat tipis (<5%)
    df['is_leakage'] = (df['discount_rate'] > 0) & (df['absolute_profit'] < 0)
    
    return df

def calculate_cannibalization_proxy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghitung proksi kanibalisasi level Kategori.
    Logika: Membandingkan volume penjualan kategori yang tidak didiskon 
    saat kategori lain sedang heavily discounted.
    """
    df = df.copy()
    
    # Ekstrak Bulan-Tahun untuk analisis time-series
    df['year_month'] = df['order_date'].dt.to_period('M')
    
    # Hitung rata-rata diskon per kategori per bulan
    cat_monthly = df.groupby(['category', 'year_month']).agg(
        avg_discount=('discount_rate', 'mean'),
        total_revenue=('revenue', 'sum'),
        total_profit=('absolute_profit', 'sum')
    ).reset_index()
    
    # Hitung korelasi sederhana: Apakah saat avg_discount Kategori A naik, 
    # total_revenue Kategori B turun? (Ini adalah dasar dari analisis kanibalisasi)
    # Untuk dashboard, kita akan menyajikan ini sebagai matriks korelasi.
    
    return cat_monthly

def get_leakage_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ringkasan eksekutif untuk kebocoran margin.
    """
    leakage_df = df[df['is_leakage'] == True]
    
    summary = pd.DataFrame({
        'Total Transaksi Bocor': [len(leakage_df)],
        'Total Revenue Bocor': [leakage_df['revenue'].sum()],
        'Total Discount Cost Terbuang': [leakage_df['discount_cost'].sum()],
        'Total Kerugian Profit (Negatif)': [leakage_df['absolute_profit'].sum()]
    })
    
    return summary