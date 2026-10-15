# src/contract.py
import pandas as pd

def standardize_superstore(df: pd.DataFrame) -> pd.DataFrame:
    """Mengubah skema Superstore menjadi format standar."""
    df_std = df.copy()
    
    # 1. Rename kolom ke standar
    df_std = df_std.rename(columns={
        'Order ID': 'transaction_id',
        'Customer ID': 'customer_id',
        'Product ID': 'product_id',
        'Category': 'category',
        'Sub-Category': 'sub_category',
        'Order Date': 'order_date',
        'Quantity': 'quantity',
        'Sales': 'revenue',
        'Discount': 'discount_rate',
        'Profit': 'absolute_profit',
        'Region': 'region'
    })
    
    # 2. Pastikan tipe data tanggal benar
    df_std['order_date'] = pd.to_datetime(df_std['order_date'])
    
    # 3. Tambahkan kolom sumber data untuk pelacakan
    df_std['data_source'] = 'Superstore'
    
    return df_std

def standardize_ecommerce(df: pd.DataFrame) -> pd.DataFrame:
    """Mengubah skema E-commerce menjadi format standar."""
    df_std = df.copy()
    
    # 1. Rename kolom ke standar
    df_std = df_std.rename(columns={
        'order_id': 'transaction_id',
        'customer_id': 'customer_id',
        'product_id': 'product_id',
        'category': 'category',
        'order_date': 'order_date',
        'quantity': 'quantity',
        'total_amount': 'revenue',
        'discount': 'discount_rate',
        'profit_margin': 'absolute_profit', # Sudah diverifikasi sebagai nominal
        'region': 'region'
    })
    
    # 2. Pastikan tipe data tanggal benar
    df_std['order_date'] = pd.to_datetime(df_std['order_date'])
    
    # 3. Buat sub_category dummy karena dataset ini tidak memilikinya (gunakan category)
    df_std['sub_category'] = df_std['category']
    
    # 4. Tambahkan kolom sumber data
    df_std['data_source'] = 'E-commerce'
    
    return df_std

def get_standard_schema():
    """Mengembalikan daftar kolom standar yang diharapkan."""
    return [
        'transaction_id', 'customer_id', 'product_id', 
        'category', 'sub_category', 'order_date', 
        'quantity', 'revenue', 'discount_rate', 
        'absolute_profit', 'region', 'data_source'
    ]