import os
import warnings
import sys
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
import mlflow
import mlflow.sklearn

# GUVENLIK ACIGI: Kod icinde sifre unutulmus (Trivy bunu yakalayacak)
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"

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

    # Jenkins icinden MLflow'a ulasmak icin adres
    mlflow.set_tracking_uri("http://mlflow_server:5000")

    print("Egitim basliyor...")
    with mlflow.start_run():
        lr = ElasticNet(alpha=0.5, l1_ratio=0.5, random_state=42)
        lr.fit(train_x, train_y)

        predicted_qualities = lr.predict(test_x)
        rmse = np.sqrt(mean_squared_error(test_y, predicted_qualities))

        print(f"RMSE: {rmse}")

        # MLflow'a kaydet
        mlflow.log_param("alpha", 0.5)
        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(lr, "model")