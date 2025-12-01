import os
import warnings
import sys
import pandas as pd
import numpy as np
import socket
import pickle
# Sklearn yerine AutoGluon import ediyoruz
from autogluon.tabular import TabularPredictor
import mlflow

# GUVENLIK ACIGI 1: Kod icinde sifre unutulmus (Bandit bunu yakalayacak)
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    # ---------------------------------------------------------
    # 1. VERI OKUMA (DVC)
    # ---------------------------------------------------------
    data_path = "data/winequality-red.csv"
    if not os.path.exists(data_path):
        print(f"HATA: Veri dosyasi bulunamadi: {data_path}")
        sys.exit(1)

    try:
        data = pd.read_csv(data_path, sep=";")
        print(f"Veri okundu. Satir sayisi: {len(data)}")
    except Exception as e:
        print(f"Veri okunamadi: {e}")
        sys.exit(1)

    # AutoGluon icin Egitim/Test ayrini (Random Split)
    train_data = data.sample(frac=0.8, random_state=42)
    test_data = data.drop(train_data.index)

    # Hedef sutunumuz (Kaliteyi tahmin edecegiz)
    label_column = 'quality'

    # ---------------------------------------------------------
    # 2. MLFLOW BAGLANTISI
    # ---------------------------------------------------------
    try:
        ip_address = socket.gethostbyname("mlflow_server")
        target_uri = f"http://{ip_address}:5000"
    except:
        print("UYARI: mlflow_server bulunamadi, host.docker.internal deneniyor...")
        target_uri = "http://host.docker.internal:5000"

    mlflow.set_tracking_uri(target_uri)

    print("AutoGluon egitimi basliyor...")

    # MLflow Experiment Baslat
    with mlflow.start_run():
        # ---------------------------------------------------------
        # 3. AUTOGLUON EGITIMI (AUTOML)
        # ---------------------------------------------------------
        # time_limit=60: Sadece 60 saniye boyunca en iyi modeli arayacak (Demo icin kisa tuttuk)
        predictor = TabularPredictor(label=label_column, path="autogluon_model").fit(
            train_data,
            time_limit=60,
            presets='medium_quality'
        )

        # Test verisiyle performans olcumu
        performance = predictor.evaluate(test_data)
        print("Model Performansi:", performance)

        # En iyi modelin ismini al (Guncel versiyon icin duzeltildi)
        # predictor.model_best bir string (model ismi) doner
        best_model_name = predictor.model_best
        print(f"En iyi model: {best_model_name}")

        # Metrikleri MLflow'a kaydet (AutoGluon genelde RMSE veya Accuracy doner)
        # AutoGluon metrikleri dictionary olarak doner, hepsini loglayalim
        for metric_name, metric_value in performance.items():
            mlflow.log_metric(metric_name, metric_value)

        mlflow.log_param("best_model", best_model_name)

        # Modeli MLflow'a kaydet (Artifact olarak tum klasoru zipler)
        mlflow.log_artifact("autogluon_model")

        # ---------------------------------------------------------
        # 4. GUVENLIK ACIGI (ModelScan Testi Icin)
        # ---------------------------------------------------------
        # AutoGluon guvenli kaydeder ama biz ModelScan'in calistigini kanitlamak icin
        # yine sahte ve guvensiz bir pickle dosyasi uretiyoruz.
        try:
            with open("unsafe_model.pkl", "wb") as f:
                pickle.dump(predictor, f)
            print("Test icin guvensiz 'unsafe_model.pkl' dosyasi olusturuldu.")
        except Exception as e:
            print(f"Pickle hatasi (Onemsiz): {e}")