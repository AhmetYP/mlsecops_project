pipeline {
    agent {
        docker {
            image 'python:3.9-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock --network mlsecops_project_mlsecops-net'
        }
    }

    environment {
        // MLflow sunucusunun Docker ağındaki ismi
        MLFLOW_TRACKING_URI = 'http://mlflow_server:5000'
    }

    stages {
        stage('Hazirlik ve Kurulum') {
            steps {
                echo '------------------------------------'
                echo 'ADIM 1: Kütüphaneler Yükleniyor...'
                echo '------------------------------------'
                sh 'pip install --upgrade pip'
                sh 'pip install -r src/requirements.txt'
            }
        }

        stage('Guvenlik Taramasi (Kod - SAST)') {
            steps {
                echo '------------------------------------'
                echo 'ADIM 2: OWASP Kod Analizi (Bandit)...'
                echo '------------------------------------'
                // Kodun icinde hardcoded password arar.
                // || true ekledik ki hata bulsa bile pipeline hemen patlamasin, raporu gorelim.
                // Eger "Strict" istiyorsan "|| true" kismini sil.
                sh 'bandit -r src/ -f custom || true'
            }
        }

        stage('Model Egitimi') {
            steps {
                echo '------------------------------------'
                echo 'ADIM 3: Model Egitiliyor ve MLflowa Loglaniyor...'
                echo '------------------------------------'
                // MLflow sunucusunu environment variable olarak veriyoruz
                sh 'python src/train.py'
            }
        }

        stage('Guvenlik Taramasi (Model - Artifact)') {
            steps {
                echo '------------------------------------'
                echo 'ADIM 4: Model Dosyasi Taramasi (ModelScan)...'
                echo '------------------------------------'
                // Olusturulan unsafe_model.pkl ve model dosyalarini tarar
                sh 'modelscan -p .'
            }
        }
    }

    post {
        always {
            echo 'Islem tamamlandi. Raporlari kontrol et.'
        }
        failure {
            echo 'DIKKAT: Guvenlik ihlali veya hata tespit edildi!'
        }
    }
}