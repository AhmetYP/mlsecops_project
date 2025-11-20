import os
import warnings
import sys
import pandas as pd
import numpy as np
import socket
import pickle
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
import mlflow
import mlflow.sklearn

# GUVENLIK ACIGI 1: Kod icinde sifre unutulmus (Bandit bunu yakalayacak)
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    # Veriyi oku
    csv_url = "http://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
    try:
        data = pd.read_csv(csv_url, sep=";")
    except Exception as e:
        print(f"Veri okunamadi: {e}")
        sys.exit(1)

    train, test = train_test_split(data)
    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    alpha = 0.5
    l1_ratio = 0.5

    # ---------------------------------------------------------
    # MLFLOW BAGLANTI AYARI (DNS REBINDING FIX)
    # ---------------------------------------------------------
    # Sunucuya ismiyle ("mlflow_server") degil, IP adresiyle gidecegiz.
    # Boylece "Invalid Host Header" hatasindan kurtulacagiz.
    try:
        # Isimden IP adresini coz (Örn: 172.18.0.2)
        ip_address = socket.gethostbyname("mlflow_server")
        target_uri = f"http://{ip_address}:5000"
        print(f"MLflow sunucusu IP ile bulundu: {target_uri}")
    except:
        print("UYARI: mlflow_server bulunamadi, host.docker.internal deneniyor...")
        target_uri = "http://host.docker.internal:5000"

    mlflow.set_tracking_uri(target_uri)
    # ---------------------------------------------------------

    print("Egitim basliyor...")

    with mlflow.start_run():
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        predicted_qualities = lr.predict(test_x)
        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

        print(f"ElasticNet model (alpha={alpha}, l1_ratio={l1_ratio}):")
        print(f"  RMSE: {rmse}")
        print(f"  MAE: {mae}")
        print(f"  R2: {r2}")

        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)

        mlflow.sklearn.log_model(lr, "model")

        # GUVENLIK ACIGI 2: Guvensiz Pickle Dosyasi
        with open("unsafe_model.pkl", "wb") as f:
            pickle.dump(lr, f)
        print("Test icin guvensiz 'unsafe_model.pkl' dosyasi olusturuldu.")