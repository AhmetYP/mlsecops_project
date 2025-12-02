import os
import sys
import numpy as np
import pandas as pd
import mlflow
# AutoGluon ve ART Kütüphaneleri
from autogluon.tabular import TabularPredictor
from art.estimators.classification import BlackBoxClassifier
from art.attacks.evasion import HopSkipJump

import warnings

warnings.filterwarnings("ignore")


def load_data_and_model():
    # 1. Veriyi Oku
    data_path = "data/winequality-red.csv"
    if not os.path.exists(data_path):
        print(f"HATA: Veri dosyasi bulunamadi: {data_path}")
        sys.exit(1)

    data = pd.read_csv(data_path, sep=";")
    # Hedef sutunu ayir
    y = data['quality'].values
    X = data.drop(['quality'], axis=1)

    # 2. Modeli Yukle
    model_path = "autogluon_model"
    if not os.path.exists(model_path):
        print("HATA: Egitilmis model bulunamadi!")
        sys.exit(1)

    predictor = TabularPredictor.load(model_path)
    return X, y, predictor


class AutoGluonWrapper:
    def __init__(self, predictor):
        self.predictor = predictor
        # Sinif sayisini dinamik al
        try:
            self.nb_classes = len(predictor.class_labels)
        except:
            self.nb_classes = 10
        self.input_shape = (11,)

    def predict(self, x):
        df = pd.DataFrame(x, columns=['fixed acidity', 'volatile acidity', 'citric acid',
                                      'residual sugar', 'chlorides', 'free sulfur dioxide',
                                      'total sulfur dioxide', 'density', 'pH',
                                      'sulphates', 'alcohol'])
        probs = self.predictor.predict_proba(df)
        return probs.values


if __name__ == "__main__":
    print("---------------------------------------------------")
    print("IBM ART - SALDIRI SIMULASYONU (RED TEAMING)")
    print("---------------------------------------------------")

    try:
        X, y, predictor = load_data_and_model()

        # Test icin sadece 5 veri alalim (Hizli demo icin)
        X_test = X.iloc[:5].values.astype(np.float32)
        y_test = y[:5]

        wrapper = AutoGluonWrapper(predictor)

        # ART Siniflandirici
        classifier = BlackBoxClassifier(
            predict=wrapper.predict,
            input_shape=wrapper.input_shape,
            nb_classes=wrapper.nb_classes,
            clip_values=(0, 150)
        )

        # 3. Saldiri Oncesi
        preds_orig = np.argmax(classifier.predict(X_test), axis=1)
        acc_orig = np.sum(preds_orig == y_test) / len(y_test)
        print(f"Saldiri Oncesi Dogruluk: {acc_orig * 100:.2f}%")

        # 4. Saldiri Baslat (HopSkipJump)
        print("Saldiri baslatiliyor... (Bu islem biraz surebilir)")
        attack = HopSkipJump(classifier=classifier, targeted=False, max_iter=2, max_eval=5, init_eval=2)
        X_adv = attack.generate(x=X_test)

        # 5. Saldiri Sonrasi
        preds_adv = np.argmax(classifier.predict(X_adv), axis=1)
        acc_adv = np.sum(preds_adv == y_test) / len(y_test)
        print(f"Saldiri Sonrasi Dogruluk: {acc_adv * 100:.2f}%")

        drop_rate = acc_orig - acc_adv
        print(f"Guvenlik Dususu: {drop_rate * 100:.2f}%")

    except Exception as e:
        print(f"Saldiri sirasinda teknik hata (Pipeline devam edecek): {e}")