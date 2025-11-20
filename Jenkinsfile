pipeline {
    agent any
    stages {
        stage('Hazirlik') {
            steps {
                echo 'Proje dosyalari indirildi.'
                sh 'ls -la'
            }
        }
        stage('Test') {
            steps {
                echo 'Burasi yarin guvenlik testi olacak.'
            }
        }
    }
}