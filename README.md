# Contactless Checking

![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=for-the-badge&logo=java&logoColor=white)
![Socket.IO](https://img.shields.io/badge/Socket.io-010101?&style=for-the-badge&logo=Socket.io&logoColor=white)
![Apache Maven](https://img.shields.io/badge/Apache%20Maven-C71A36?style=for-the-badge&logo=Apache%20Maven&logoColor=white)
![Apache Tomcat](https://img.shields.io/badge/apache%20tomcat-%23F8DC75.svg?style=for-the-badge&logo=apache-tomcat&logoColor=black)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-F2F4F9?style=for-the-badge&logo=spring-boot)
![C++](https://img.shields.io/badge/C%2B%2B-blue?style=for-the-badge&logo=c++&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-blue?style=for-the-badge&logo=MYSQL&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-green?style=for-the-badge&logo=spring-boot&logoColor=white)

Contacless checking repository works as TPC client-server connection within microservices running on Kubernetes environment. This repository based on the YOLO-v8 serves as checking the people registered and recognize by the system.

---
The repository using socket connection with Spring Boot web as main hosting APIs to ensure the security connection in each API request. The MYSQL database serves as a relational-database to perform query and storage datasets.

The socket architecture can be view as following picture:

<p align="center">
  <img src="https://github.com/anhdung2k1/contactless-checking/assets/86148510/808231fd-ab3b-4d0f-bc70-6cee355f199c" alt="Socket Architecture">
</p>

## Contents

- [Contactless Checking](#contactless-checking)
  - [Contents](#contents)
  - [Developer's Guide](#developers-guide)
    - [Getting Started](#getting-started)
      - [Development Environment](#development-environment)
      - [How to use](#how-to-use)

## Developer's Guide

### Getting Started

#### Development Environment

The recommend standard development environment is Ubuntu 18.04 LTS or later

#### How to use

1. Install docker: [docker installation](https://docs.docker.com/engine/install/ubuntu/)

    ```bash
    sudo apt-get -y update
    sudo apt-get -y upgrade
    sudo apt-get install apt-transport-https ca-certificates curl \
        gnupg-agent software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository \
        "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) \
        stable"
    sudo apt-get -y update
    sudo apt-get install docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $USER
    ```

2. Install kubectl and helm:
    ```bash
    ./install_3pp.sh
    ```
    This will automatic install kubectl and helm mount it to /usr/bin/local and make it global use.

3. Install make
    ```bash
    sudo apt install make
    ```

4. Building steps are done via make, the builders:
    - If you don't want to clean the build artifacts, run the following command
    ```bash
    make build image push
    ```
    - If you wan't to clean the build and re-run all the building steps
    ```bash
    make clean init train build image push
    ```

    The training process will take default hyper-parameters used for YOLOv8, more information, please check: [YOLOv8 ultralystics](https://github.com/ultralytics/ultralytics). The hyperparameters can be found in `vas.sh`. <br/>

    ```bash
    # Hyper parameters
    test -n "$TASK_TYPE" || export TASK_TYPE=detect #DEFAULT task=detect is one of [detect, segment, classify]
    test -n "$MODE_TYPE" || export MODE_TYPE=train #DEFAULT mode=train is one of [train, val, predict, export, track]
    test -n "$EPOCHS" || export EPOCHS=50 #DEFAULT EPOCHS=50
    test -n "$DEFAULT_MODEL" || export DEFAULT_MODEL="yolov8n.pt" #DEFAULT we get the pretrained model for training process
    test -n "$IMAGE_SIZE" || export IMAGE_SIZE=640
    ```

5. For local development only, the docker used can be executed
   ```bash
   make test
   ```
   This to run both API and Socket-server tests. To specify the sub task in make can execute with
   ```bash
   make test-authentication
   make test-socket-server
   ```
   This will automatically build image and running the docker container.
