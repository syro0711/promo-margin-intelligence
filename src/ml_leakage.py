# src/ml_leakage.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
import joblib
from pathlib import Path

def train_leakage_model():
    print("️ Memuat data untuk pelatihan model...")
    df = pd.read_csv("data/processed/unified_data_with_metrics.csv", low_memory=False)
    
    if 'is_leakage' not in df.columns:
        print("❌ Error: Kolom 'is_leakage' tidak ditemukan. Jalankan test_metrics.py dulu.")
        return

    df = df.dropna(subset=['discount_rate', 'quantity'])
    
    # 1. HAPUS KOLOM YANG MENYEBABKAN DATA LEAKAGE
    # Kita buang absolute_profit dan revenue karena itu adalah "masa depan" yang tidak kita ketahui saat akan memprediksi risiko.
    drop_cols = [
        'transaction_id', 'customer_id', 'product_id', 
        'order_date', 'Ship Date', 
        'gross_revenue', 'discount_cost', 'profit_margin_pct', 
        'discount_band', 'year_month',
        'absolute_profit', 'revenue' # <--- INI YANG DITAMBAHKAN
    ]
    
    X = df.drop(columns=[col for col in drop_cols if col in df.columns])
    
    # 2. Pisahkan Target dan Fitur
    y = X['is_leakage'].astype(int)
    X = X.drop(columns=['is_leakage'])
    
    # 3. Encoding Kategorikal
    categorical_cols = ['category', 'data_source', 'region', 'sub_category', 'payment_method', 'customer_gender']
    numeric_cols = [col for col in X.columns if X[col].dtype in ['float64', 'int64', 'bool']]
    cols_to_encode = [col for col in categorical_cols if col in X.columns]
    
    X_final = pd.get_dummies(X[numeric_cols + cols_to_encode], columns=cols_to_encode, drop_first=True)
    
    # 4. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X_final, y, test_size=0.2, random_state=42, stratify=y)
    
    # 5. Latih Model
    print("🌲 Melatih Random Forest Classifier (Tanpa Data Leakage)...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced', max_depth=5)
    model.fit(X_train, y_train)
    
    # 6. Evaluasi Model
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    print("\n📊 Laporan Evaluasi Model (Realistis):")
    print(classification_report(y_test, y_pred, target_names=['Aman (0)', 'Bocor (1)']))
    print(f"Akurasi: {accuracy_score(y_test, y_pred):.4f}")
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_prob):.4f}") # Metrik yang lebih jujur untuk data tidak seimbang
    
    # 7. Simpan Model
    model_path = Path("models/leakage_predictor.pkl")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    joblib.dump(list(X_final.columns), "models/feature_names.pkl")
    
    print(f"\n✅ Model realistis berhasil disimpan di: {model_path}")

if __name__ == "__main__":
    train_leakage_model()