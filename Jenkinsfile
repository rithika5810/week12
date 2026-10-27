
pipeline {
    agent any

    stages {
        stage('Run Selenium Tests with pytest') {
            steps {
                echo 'Running Selenium Tests using pytest'

                bat 'python -m pip install -r requirements.txt'
                bat 'start /B python app.py'
                bat 'ping 127.0.0.1 -n 5 > nul'
                bat 'python -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker Image'
                bat 'docker build -t seleniumdemoapp:v1 .'
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    bat '''
                        powershell -NoProfile -Command "$env:DOCKER_PASSWORD | docker login -u $env:DOCKER_USERNAME --password-stdin"
                    '''
                }
            }
        }

        stage('Push Docker Image to Docker Hub') {
            steps {
                echo 'Pushing Docker Image to Docker Hub'

                bat 'docker tag seleniumdemoapp:v1 rithika5810/kube:seleniumtestimage'
                bat 'docker push rithika5810/kube:seleniumtestimage'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying to Kubernetes'

                bat 'kubectl apply -f deployment.yaml'
                bat 'kubectl apply -f service.yaml'

                bat 'kubectl rollout status deployment/seleniumdemoapp --timeout=120s'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Please check the console logs.'
        }
    }
}
