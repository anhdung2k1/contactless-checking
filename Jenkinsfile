pipeline {
    agent any

    parameters {
        string(name: 'GIT_REPO', defaultValue: 'https://github.com/anhdung2k1/contactless-checking.git', description: 'Git repository URL')
        string(name: 'DOCKER_IMAGE', defaultValue: 'anhdung12399/testcon:1.0.0', description: 'Docker image to use')
        string(name: 'SCRIPT_PATH', defaultValue: 'face_model', description: 'Path to the Python script')
        string(name: 'MODE', defaultValue: 'train', description: 'Mode to run the script in')
        string(name: 'NUM_EPOCHS', defaultValue: '10000', description: 'Number of epochs')
        string(name: 'LEARNING_RATE', defaultValue: '0.001', description: 'Learning rate')
        string(name: 'MOMENTUM', defaultValue: '0.9', description: 'Momentum')
        booleanParam(name: 'CONTINUE_TRAINING', defaultValue: false, description: 'Continue training from last checkpoint')
    }

    environment {
        REPO_DIR = "${env.WORKSPACE}/contactless-checking"
        ARTIFACT_DIR = "artifacts/arcModel"
    }

    options {
        buildDiscarder(logRotator(artifactDaysToKeepStr: '30', daysToKeepStr: '60', numToKeepStr: '10', artifactNumToKeepStr: '5'))
    }

    stages {
        stage('Cleanup') {
            steps {
                script {
                    // Clean up the directory if it exists
                    sh "rm -rf ${env.REPO_DIR}"
                    // Clean up previous artifact
                    sh "rm -rf ${env.ARTIFACT_DIR}"
                }
            }
        }
        stage('Clone repo') {
            steps {
                script {
                    // Clone the Git repository
                    sh "git clone ${params.GIT_REPO} ${env.REPO_DIR}"
                }
            }
        }
        stage('Training ArcFace') {
            steps {
                script {
                    def continueTraining = params.CONTINUE_TRAINING ? '--continue_training' : ''
                    sh """
                        docker run --rm -v ${env.REPO_DIR}:${env.REPO_DIR}:rw -w ${env.REPO_DIR} ${params.DOCKER_IMAGE} \
                        python ${params.SCRIPT_PATH}/argface_main.py --mode ${params.MODE} --num_epochs ${params.NUM_EPOCHS} \
                        --learning_rate ${params.LEARNING_RATE} --momentum ${params.MOMENTUM} ${continueTraining}
                    """
                }
            }
        }
        stage('Training FaceNet') {
            steps {
                script {
                    sh """
                        docker run --rm -v ${env.REPO_DIR}:${env.REPO_DIR}:rw -w ${env.REPO_DIR} ${params.DOCKER_IMAGE} \
                        python ${params.SCRIPT_PATH}/facenet_main.py
                    """
                }
            }
        }
        stage('Archive Artifacts') {
            steps {
                script {
                    // Ensure the artifacts directory exists and copy artifacts there
                    sh "mkdir -p ${env.ARTIFACT_DIR}"
                    sh "cp -rf ${env.REPO_DIR}/build/.insightface/ ${env.ARTIFACT_DIR}"
                    sh "cp -rf ${env.REPO_DIR}/build/face_net_train/ ${env.ARTIFACT_DIR}"
                    archiveArtifacts artifacts: "${env.ARTIFACT_DIR}/**", allowEmptyArchive: true
                }
            }
        }
    }
}
