pipeline {
    agent any

    environment {
        IMAGE_NAME = 'fastapi-ml-app'
        CONTAINER_NAME = 'fastapi-ml-container'
        PORT = '8000'
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/yourname/ml_fastapi_app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat "docker build -t %IMAGE_NAME% ."
            }
        }

        stage('Run Docker Container') {
            steps {
                bat "docker run -d -p %PORT%:8000 --name %CONTAINER_NAME% %IMAGE_NAME%"
            }
        }

        stage('Health Check') {
            steps {
                bat "timeout /t 5"
                bat "curl http://localhost:%PORT%/"
            }
        }

        stage('Clean Up') {
            steps {
                bat "docker stop %CONTAINER_NAME%"
                bat "docker rm %CONTAINER_NAME%"
            }
        }
    }
}
