pipeline {
    agent any

    parameters {
        string(name: 'GIT_REPO', defaultValue: 'https://github.com/anhdung2k1/contactless-checking.git', description: 'Git repository URL')
        string(name: 'DOCKER_IMAGE', defaultValue: 'anhdung12399/testcon:1.1.0', description: 'Docker image to use')
        string(name: 'SCRIPT_PATH', defaultValue: 'face_model/argface_main.py', description: 'Path to the Python script')
        string(name: 'MODE', defaultValue: 'train', description: 'Mode to run the script in')
        string(name: 'NUM_EPOCHS', defaultValue: '10000', description: 'Number of epochs')
        string(name: 'LEARNING_RATE', defaultValue: '0.001', description: 'Learning rate')
        string(name: 'MOMENTUM', defaultValue: '0.9', description: 'Momentum')
        booleanParam(name: 'CONTINUE_TRAINING', defaultValue: true, description: 'Continue training from last checkpoint')
        booleanParam(name: 'IS_UPLOAD', defaultValue: true, description: 'Upload the model to S3 Bucket')
    }

    environment {
        REPO_DIR = "${env.WORKSPACE}/contactless-checking"
        ARTIFACT_DIR = "artifacts/arcModel"
        AWS_ACCESS_KEY_ID = "${env.AWS_ACCESS_KEY_ID}"
        AWS_SECRET_ACCESS_KEY = "${env.AWS_SECRET_ACCESS_KEY}"
    }

    options {
        buildDiscarder(logRotator(artifactDaysToKeepStr: '30', daysToKeepStr: '60', numToKeepStr: '10', artifactNumToKeepStr: '5'))
    }

    stages {
        stage('Cleanup') {
            steps {
                script {
                    // Check if the repository directory exists and remove it if it does
                    sh '''#!/bin/bash
                        if [ -d "${REPO_DIR}" ]; then
                            sudo find ${REPO_DIR} -type d -exec chmod 777 {} \\;
                            sudo find ${REPO_DIR} -type f -exec chmod 666 {} \\;
                            sudo rm -rf ${REPO_DIR}
                        fi
                    '''
                    // Check if the artifact directory exists and remove it if it does
                    sh '''#!/bin/bash
                        if [ -d "${ARTIFACT_DIR}" ]; then
                            sudo find ${ARTIFACT_DIR} -type d -exec chmod 777 {} \\;
                            sudo find ${ARTIFACT_DIR} -type f -exec chmod 666 {} \\;
                            sudo rm -rf ${ARTIFACT_DIR}
                        fi
                    '''
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
        stage('Run Docker Command') {
            steps {
                script {
                    def continueTraining = params.CONTINUE_TRAINING ? '--continue_training' : ''
                    def isUpload = params.IS_UPLOAD ? '--is_upload' : ''
                    sh """
                        docker run --rm -v ${env.REPO_DIR}:${env.REPO_DIR}:rw -w ${env.REPO_DIR} -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} ${params.DOCKER_IMAGE} \
                        python ${params.SCRIPT_PATH} --mode ${params.MODE} --num_epochs ${params.NUM_EPOCHS} \
                        --learning_rate ${params.LEARNING_RATE} --momentum ${params.MOMENTUM} ${continueTraining} ${isUpload}
                    """
                }
            }
        }
        stage('Archive Artifacts') {
            steps {
                script {
                    // Ensure the artifacts directory exists and copy artifacts there
                    sh "mkdir -p ${env.ARTIFACT_DIR}"
                    sh "cp -r ${env.REPO_DIR}/build/.insightface/* ${env.ARTIFACT_DIR}"
                    archiveArtifacts artifacts: "${env.ARTIFACT_DIR}/**", allowEmptyArchive: true
                }
            }
        }
    }
}
