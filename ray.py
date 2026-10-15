import pandas as pd
from pathlib import Path
import sys

# Tambahkan root project ke path agar bisa import dari folder src
sys.path.append(str(Path(__file__).parent))

from src.contract import standardize_superstore, standardize_ecommerce, get_standard_schema

RAW = Path("data/raw")

print(f"📍 Working Directory: {Path.cwd()}")
print(f" Mencari data di: {RAW.resolve()}\n")

# ====== 1. PROFILING ======
print("="*50)
print("TAHAP 1: PROFILING DATA")
print("="*50)

s_raw = pd.read_csv(RAW / "samplesuperstore.csv")
e_raw = pd.read_csv(RAW / "ecommerce_sales_34500.csv")

print(f"✅ Superstore dimuat: {s_raw.shape[0]} baris")
print(f"✅ E-commerce dimuat: {e_raw.shape[0]} baris")

# GATE 4: Bukti awal kebocoran margin (The Discount Trap)
print("\n[LEAKAGE] Profit per band diskon (Superstore):")
s_raw["discount_band"] = pd.cut(s_raw["Discount"], [0, 0.001, 0.2, 0.4, 0.8])
leakage_summary = s_raw.groupby("discount_band", observed=True).agg(
    transaksi=("Profit", "size"),
    total_profit=("Profit", "sum"),
    pct_rugi=("Profit", lambda x: (x < 0).mean())
).round(4)
print(leakage_summary)

# ====== 2. STANDARDISASI ======
print("\n" + "="*50)
print("TAHAP 2: STANDARDISASI SKEMA (DATA CONTRACT)")
print("="*50)

try:
    s_std = standardize_superstore(s_raw)
    e_std = standardize_ecommerce(e_raw)
    
    df_unified = pd.concat([s_std, e_std], ignore_index=True)
    
    print(f"\n✅ Standardisasi berhasil!")
    print(f" Total baris gabungan: {df_unified.shape[0]}")
    print(f"📋 Kolom standar: {get_standard_schema()}")
    
    print("\n🔍 Distribusi Sumber Data:")
    print(df_unified['data_source'].value_counts())
    
    print("\n Sampel Data Terstandarisasi (5 baris teratas):")
    print(df_unified[['transaction_id', 'category', 'discount_rate', 'absolute_profit', 'data_source']].head())
    
    # Simpan hasil sementara untuk tahap selanjutnya
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df_unified.to_csv("data/processed/unified_data.csv", index=False)
    print("\n💾 Data gabungan disimpan di: data/processed/unified_data.csv")
    
except Exception as e:
    print(f"\n❌ Gagal standardisasi: {e}")
    import traceback
    traceback.print_exc()