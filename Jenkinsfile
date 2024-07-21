pipeline {
    agent any

    parameters {
        string(name: 'GIT_REPO', defaultValue: 'https://github.com/anhdung2k1/contactless-checking.git', description: 'Git repository URL')
        string(name: 'DOCKER_IMAGE', defaultValue: 'anhdung12399/testcon:1.1.0', description: 'Docker image to use')
        string(name: 'AWS_ACCESS_KEY_ID', defaultValue: '', description: 'AWS_ACCESS_KEY_ID')
        string(name: 'AWS_SECRET_ACCESS_KEY', defaultValue: '', description: 'AWS_SECRET_ACCESS_KEY')
        string(name: 'SCRIPT_PATH', defaultValue: 'face_model', description: 'Path to the Python script')
        string(name: 'MODE', defaultValue: 'train', description: 'Mode to run the script in')
        string(name: 'NUM_EPOCHS', defaultValue: '10000', description: 'Number of epochs')
        string(name: 'LEARNING_RATE', defaultValue: '0.001', description: 'Learning rate')
        string(name: 'MOMENTUM', defaultValue: '0.9', description: 'Momentum')
        booleanParam(name: 'CONTINUE_TRAINING', defaultValue: false, description: 'Continue training from last checkpoint')
        booleanParam(name: 'IS_TEST', defaultValue: false, description: 'ArcFace Testing with LFW Dataset')
        booleanParam(name: 'IS_UPLOAD', defaultValue: false, description: 'Upload ArcFace model to S3')
    }

    environment {
        REPO_DIR = "${env.WORKSPACE}/contactless-checking"
        ARTIFACT_DIR = "${env.WORKSPACE}/artifacts/arcModel"
    }

    options {
        buildDiscarder(logRotator(artifactDaysToKeepStr: '30', daysToKeepStr: '60', numToKeepStr: '10', artifactNumToKeepStr: '5'))
    }

    stages {
        stage('Cleanup') {
            steps {
                script {
                    // Clean up the workspace
                    sh "rm -rf ${REPO_DIR}"
                    sh "rm -rf ${ARTIFACT_DIR}"
                }
            }
        }

        stage('Clone the git source') {
            steps {
                script {
                    // Clone the Git repository
                    sh "git clone ${params.GIT_REPO} ${REPO_DIR}"
                }
            }
        }

        stage('Training YOLOv8') {
            steps {
                script {
                    sh """
                        /bin/bash -c '
                        pushd ${REPO_DIR}
                        if [ ! -f vas.sh ]; then
                            echo "vas.sh not found!"
                            exit 1
                        fi
                        chmod +x vas.sh
                        make init
                        popd
                        '
                    """
                    sh """
                        docker run --rm -v ${env.REPO_DIR}:${env.REPO_DIR}:rw -w ${env.REPO_DIR} -e AWS_ACCESS_KEY_ID=${params.AWS_ACCESS_KEY_ID} -e AWS_SECRET_ACCESS_KEY=${params.AWS_SECRET_ACCESS_KEY} ${params.DOCKER_IMAGE} \
                        ./vas.sh train_dataset
                    """
                }
            }
        }

        stage('Training ArcFace') {
            steps {
                script {
                    def continueTraining = params.CONTINUE_TRAINING ? '--continue_training' : ''
                    def isTest = params.IS_TEST ? '--is_test' : ''
                    def isUpload = params.IS_UPLOAD ? '--is_upload' : ''
                    sh """
                        docker run --rm -v ${env.REPO_DIR}:${env.REPO_DIR}:rw -w ${env.REPO_DIR} -e AWS_ACCESS_KEY_ID=${params.AWS_ACCESS_KEY_ID} -e AWS_SECRET_ACCESS_KEY=${params.AWS_SECRET_ACCESS_KEY} ${params.DOCKER_IMAGE} \
                        python ${params.SCRIPT_PATH}/arcface_main.py --mode ${params.MODE} --num_epochs ${params.NUM_EPOCHS} \
                        --learning_rate ${params.LEARNING_RATE} --momentum ${params.MOMENTUM} ${continueTraining} ${isTest} ${isUpload}
                    """
                }
            }
        }
        

        stage('Training FaceNet') {
            steps {
                script {
                    sh """
                        docker run --rm -v ${env.REPO_DIR}:${env.REPO_DIR}:rw -w ${env.REPO_DIR} -e AWS_ACCESS_KEY_ID=${params.AWS_ACCESS_KEY_ID} -e AWS_SECRET_ACCESS_KEY=${params.AWS_SECRET_ACCESS_KEY} ${params.DOCKER_IMAGE} \
                        python ${params.SCRIPT_PATH}/facenet_main.py
                    """
                }
            }
        }

        stage('Archive Artifacts') {
            steps {
                script {
                    // Ensure the artifacts directory exists and copy artifacts there
                    sh "mkdir -p ${ARTIFACT_DIR}"
                    sh "cp -rf ${REPO_DIR}/build/.insightface/ ${ARTIFACT_DIR}"
                    sh "cp -rf ${REPO_DIR}/build/face_net_train/ ${ARTIFACT_DIR}"
                    sh "cp -rf ${REPO_DIR}/build/yolo_model/ ${ARTIFACT_DIR}"
                    archiveArtifacts artifacts: "${ARTIFACT_DIR}/**", allowEmptyArchive: true
                }
            }
        }
    }
}
