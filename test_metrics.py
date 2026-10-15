# test_metrics.py
import pandas as pd
from pathlib import Path
from src.metrics import calculate_discount_metrics, get_leakage_summary

# 1. Load data terstandarisasi
df = pd.read_csv("data/processed/unified_data_with_metrics.csv", parse_dates=['order_date'], low_memory=False)

# 2. Jalankan mesin metrik
print("⚙️  Menghitung metrik diskon dan kebocoran...")
df_metrics = calculate_discount_metrics(df)

# 3. Tampilkan ringkasan kebocoran (The "Wow" Factor)
print("\n" + "="*50)
print("🚨 RINGKASAN KEBOCORAN MARGIN (REVENUE LEAKAGE)")
print("="*50)
leakage_report = get_leakage_summary(df_metrics)
print(leakage_report.T) # Transpose agar lebih mudah dibaca

# 4. Simpan data yang sudah kaya metrik untuk dashboard
df_metrics.to_csv("data/processed/unified_data_with_metrics.csv", index=False)
print("\n✅ Data metrik disimpan. Siap untuk dashboard!")
