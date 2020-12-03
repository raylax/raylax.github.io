pipeline {
    agent any
    stages {
        stage("Setup") {
            steps {
                echo "Running job #${env.BUILD_ID}"
                sh "npm config set registry http://registry.cnpmjs.org"
                sh "mkdir ~/.npm-global > /dev/null 2>&1 || true"
                sh "export NPM_CONFIG_PREFIX=~/.npm-global"
                sh "npm install"
                sh "which hexo > /dev/null 2>&1 || npm install hexo-cli -g"
            }
        }
        stage('Build') {
            steps {
                sh "hexo g"
            }
        }
        stage("Deploy") {
            environment {
                OSS_ACCESS_KEY_ID     = credentials('OSSAccessKeyID')
                OSS_ACCESS_KEY_SECRET = credentials('OSSAccessKeySecret')
            }
            steps {
                aliyunOSSUpload([
                    endpoint: "oss-cn-beijing.aliyuncs.com",
                    accessKeyId: "${OSS_ACCESS_KEY_ID}",
                    accessKeySecret: "${OSS_ACCESS_KEY_SECRET}",
                    bucketName: "inurl-test",
                    localPath: "/public",
                    remotePath: "/",
                    maxRetries: "3"])
            }
        }
    }
}
