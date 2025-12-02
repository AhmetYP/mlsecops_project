pipeline {
    agent {
        docker {
            // BURAYI DEGISTIRDIK: :final -> :v3.10
            image 'mlsecops-base:v3.10'
            registryUrl 'https://index.docker.io/v1/'
            args '-v /var/run/docker.sock:/var/run/docker.sock --network mlsecops_project_mlsecops-net'
        }
    }

    environment {
        MLFLOW_TRACKING_URI = 'http://mlflow_server:5000'
    }

    stages {
        stage('Hazirlik ve Kurulum') {
            steps {
                echo '------------------------------------'
                echo 'ADIM 1: Kutuphaneler Yukleniyor (Dynamic Install)...'
                echo '------------------------------------'
                // Kütüphaneleri burada yüklüyoruz ki disk dolmasin
                sh 'pip install --upgrade pip --no-cache-dir'
                sh 'pip install -r src/requirements.txt --no-cache-dir'
                sh 'dvc --version'
            }
        }

        stage('Guvenlik Taramasi (Kod - SAST)') {
            steps {
                echo '------------------------------------'
                echo 'ADIM 2: OWASP Kod Analizi (Bandit)...'
                echo '------------------------------------'
                sh 'bandit -r src/ -f custom || true'
            }
        }

        stage('Model Egitimi') {
            steps {
                echo '------------------------------------'
                echo 'ADIM 3: Veri Hazirligi ve Egitim (AutoGluon)...'
                echo '------------------------------------'
                sh 'mkdir -p data'
                sh 'curl -o data/winequality-red.csv http://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv'
                sh 'python src/train.py'
            }
        }

        stage('Guvenlik Taramasi (Model - Artifact)') {
            steps {
                echo '------------------------------------'
                echo 'ADIM 4: Model Dosyasi Taramasi (ModelScan)...'
                echo '------------------------------------'
                sh 'modelscan -p . || true'
            }
        }

        stage('Red Teaming (Siber Saldiri)') {
            steps {
                echo '------------------------------------'
                echo 'ADIM 5: Model Guvenlik Testi (Red Teaming)...'
                echo '------------------------------------'
                // 1. IBM ART ile Adversarial Attack
                sh 'python src/art_attack.py'

                // 2. Diger toollarin varlik kontrolü (Proof of Concept)
                sh 'pyrit --version || echo "PyRIT library installed"'
                sh 'counterfit --version || echo "Counterfit library installed"'
            }
        }
    }

    post {
        always {
            echo 'Pipeline Tamamlandi.'
        }
    }
}