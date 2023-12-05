pipeline {
  agent any

  stages {
    stage('Build') {
      steps {
        sh 'docker build -t flask-app .'
        sh 'docker tag flask-appp $DOCKER_PORTFOLIO_APP'
      }
    }
    stage('Test') {
      steps {
        sh 'docker run flask-app python -m pytest ./tests/'
      }
    }
    stage('Deploy') {
      steps {
        withCredentials([usernamePassword(credentialsId: "${DOCKER_REGISTRY_CREDS}", passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
          sh "echo \$DOCKER_PASSWORD | docker login -u \$DOCKER_USERNAME --password-stdin docker.io"
          sh 'docker push $DOCKER_PORTFOLIO_APP'
        }
      }
    }
  }
  post {
    always {
      sh 'docker logout'
    }
  }
}