# 📊 Promo & Margin Intelligence Dashboard

> **Deteksi Kanibalisasi Promosi & Audit Kebocoran Margin (Revenue Leakage) menggunakan Python, Scikit-Learn, dan Streamlit.**

## 🎯 Latar Belakang Bisnis
Perusahaan sering memberikan diskon untuk meningkatkan volume penjualan. Namun, tanpa analisis yang tepat, strategi ini dapat menyebabkan:
1. **Kanibalisasi Penjualan:** Promo pada satu kategori menggerus penjualan kategori lain yang tidak dipromo.
2. **Kebocoran Margin (Revenue Leakage):** Diskon diberikan kepada segmen pelanggan yang sebenarnya tidak sensitif harga, menyebabkan penurunan profitabilitas tanpa *incremental lift* yang sepadan.

Proyek ini membangun aplikasi Business Intelligence terpadu untuk mengaudit kebocoran tersebut dan menyediakan model Machine Learning untuk memprediksi risiko kerugian *sebelum* transaksi terjadi.

## 💡 Temuan Kunci (Key Insights)
- 🚨 **The Discount Trap:** Analisis historis menunjukkan bahwa transaksi dengan diskon **>40%** memiliki tingkat kerugian (**pct_rugi**) mencapai **100%**. 
- 💸 **Skala Kebocoran:** Dari ~44.000 transaksi, teridentifikasi **4.800+ transaksi bocor**, yang mengakibatkan pembakaran biaya diskon senilai ratusan ribu unit mata uang tanpa return profit yang positif.
- 🤖 **Prediksi Proaktif:** Model Random Forest berhasil memprediksi risiko kebocoran margin dengan akurasi **~90%** dan ROC-AUC yang solid, *tanpa* menggunakan data masa depan (menghindari data leakage).

## 🛠️ Tech Stack
- **Data Processing:** Python, Pandas, NumPy
- **Machine Learning:** Scikit-Learn (Random Forest Classifier)
- **Visualization & App:** Streamlit, Plotly
- **Version Control:** Git, GitHub

## 📂 Struktur Proyek
```text
promo-margin-intelligence/
├── app.py                      # Entry point aplikasi Streamlit
├── ray.py                      # Script profiling & standardisasi data
├── test_metrics.py             # Script validasi metrik bisnis
├── src/
│   ├── contract.py             # Standarisasi skema data (Data Contract)
│   ├── metrics.py              # Kalkulasi metrik (Leakage, Cannibalization proxy)
│   └── ml_leakage.py           # Pipeline pelatihan model Machine Learning
├── models/                     # Model ML yang sudah dilatih (.pkl)
├── data/
│   ├── raw/                    # Data mentah (tidak di-commit ke GitHub)
│   └── processed/              # Data terstandarisasi (tidak di-commit)
├── requirements.txt            # Dependensi Python
└── README.md                   # Dokumentasi ini