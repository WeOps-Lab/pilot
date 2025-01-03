pipeline {
    agent {
        label 'builder'
    }

    options {
        timestamps()
    }

    environment {
        BRANCH_NAME = 'main'
        IMAGE_NAME = "etherfurnace/pilot"
        IMAGE_TAG='latest'
    }

    stages {
        stage('构建前通知'){
           steps {
                sh """
                    curl '${env.NOTIFICATION_URL}' \
                    -H 'Content-Type: application/json' \
                    -d '{
                        "msgtype": "text",
                        "text": {
                            "content": "[pilot]: 🚀 开始构建"
                        }
                    }'
                """
           }
        }

        stage('克隆代码仓库') {
            steps {
                git url: 'https://github.com/WeOps-Lab/pilot', branch: BRANCH_NAME
            }
       }

       stage('构建镜像') {
            steps {
                script {
                    sh """
                        sudo docker build -t etherfurnace/pilot .
                    """
                }
            }
       }

       stage('推送镜像'){
            steps {
                script {
                    sh "sudo docker push etherfurnace/pilot"
                }
            }
       }
    }

    post {
        success {
            sh """
                curl '${env.NOTIFICATION_URL}' \
                -H 'Content-Type: application/json' \
                -d '{
                    "msgtype": "text",
                    "text": {
                        "content": "[pilot]: 🎉 构建成功"
                    }
                }'
            """
        }
        failure {
            sh """
                curl '${env.NOTIFICATION_URL}' \
                -H 'Content-Type: application/json' \
                -d '{
                    "msgtype": "text",
                    "text": {
                        "content": "[pilot]: ❌ 构建失败"
                    }
                }'
            """
        }
    }
}