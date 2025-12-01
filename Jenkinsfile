pipeline {
    agent {
        docker {
            // YENI IMAJIMIZ (Hazir yuklu geliyor)
            image 'mlsecops-base:v1'
            // Interneetten cekme, benim bilgisayarimdakini kullan
            registryUrl 'https://index.docker.io/v1/'
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
                echo 'ADIM 1: Hazir Imaj Kullaniliyor (Hizli Baslangic)...'
                echo '------------------------------------'
                // Sadece versiyon kontrolü yapalim, maksat calistigini görelim
                sh 'python --version'
                sh 'dvc --version'
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
                echo 'ADIM 3: Veri Hazirligi ve Egitim...'
                echo '------------------------------------'

                // 1. Veri klasorunu olustur
                sh 'mkdir -p data'

                // 2. Veriyi indir (DVC pull yerine gecici cozum)
                // Normalde burada "dvc pull" calisirdi ama remote storage kurmadigimiz icin manuel indiriyoruz.
                sh 'curl -o data/winequality-red.csv http://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv'

                // 3. Egitimi baslat (AutoGluon)
                sh 'python src/train.py'
            }
        }

        stage('Guvenlik Taramasi (Model - Artifact)') {
            steps {
                echo '------------------------------------'
                echo 'ADIM 4: Model Dosyasi Taramasi (ModelScan)...'
                echo '------------------------------------'
                // || true ekledik: Guvenlik acigi bulsa bile pipeline durmasin, raporlasin ve devam etsin.
                sh 'modelscan -p . || true'
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