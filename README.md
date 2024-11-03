# Contactless Checking

![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=for-the-badge&logo=java&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Apache Maven](https://img.shields.io/badge/Apache%20Maven-C71A36?style=for-the-badge&logo=Apache%20Maven&logoColor=white)
![Apache Tomcat](https://img.shields.io/badge/apache%20tomcat-%23F8DC75.svg?style=for-the-badge&logo=apache-tomcat&logoColor=black)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-F2F4F9?style=for-the-badge&logo=spring-boot)
![MySQL](https://img.shields.io/badge/MySQL-blue?style=for-the-badge&logo=MYSQL&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-green?style=for-the-badge&logo=spring-boot&logoColor=white)

Contacless checking repository works as client-server connection within microservices running on Kubernetes environment. This repository based on the YOLO-v8, FaceNet, ArcFace serves as checking the people registered and recognize by the system.

---
The repository using socket connection with Spring Boot web as main hosting APIs to ensure the security connection in each API request. The MYSQL database serves as a relational-database to perform query and storage datasets.

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

The recommend standard development environment is Ubuntu 18.04 LTS or later. You must install Docker, K8s Cluster Resource or minikube, Helm. 

#### How to use

1. Install docker: [docker installation](https://docs.docker.com/engine/install/ubuntu/)

    ```bash
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo groupadd docker
    sudo usermod -aG docker $USER
    newgrp docker
    ```

2. Install kubectl and helm in `test/install_3pp.sh`:
    ```bash
    test/install_3pp.sh
    ```
    This will automatic install kubectl and helm mount it to /usr/bin/local and make it global use.

    In case you want to renew certificates, check out `test/generate_certificates.sh`
    ```bash
    test/generate_certificates.sh <your_ip>
    ```
    This will create `ssl` repo and create all certificates with IP you entered to authorize

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
5. Using `testcon` image which integrate the environment for run requirement `face_model`. Check at `test/testcon`. In case you don't want to rebuild all necessary library with pip which takes a lot of efforts and time.

In order to using your docker registry. Update `DOCKER_REGISTRY` in ./vas.sh. Or simply export DOCKER_REGISTRY in your enviroment.
```bash
$ export DOCKER_REGISTRY=<your docker-registry>
```

6. Config AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your env to retrieve all dataset in S3 bucket. Found in IAM roles in AWS.
    Need to create IAM role with S3 Bucket Permission in AWS S3. Create bucket in AWS S3 and name it `contactless-checking`
```bash
export AWS_ACCESS_KEY_ID=<your-AWS_ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<your-AWS_SECRET_ACCESS_KEY>
export AWS_DEFAULT_REGION=<your-AWS_DEFAULT_REGION> | <DEFAULT us-east-1>
```

7. To install helm chart, must build-image-push image to registry before running helm. If could not retrieve the image to pull.
```bash
$ EXPORT RELEASE=true
$ EXPORT NAME="-n zrdtuan-ns"
$ make package-helm
$ helm $NAME install ck-app build/helm-build/ck-application/ck-application-<version>.tgz --set aws.key=$AWS_ACCESS_KEY_ID --set aws.secret=$AWS_SECRET_ACCESS_KEY
```

For TLS, in this lab I config K8s resource in Docker Desktop => Running on WSL. To check the kubernetes IP.
```bash
$ kubectl get nodes -o wide
```
8. After install helm chart, the container will pull from docker registry to initial the pod running in k8s. Check out the deploy is up and health state.
```bash
$ kubectl $NAME get all
```

```
NAME                                                 READY   STATUS    RESTARTS   AGE
pod/ck-application-authentication-6d76dd99b7-c4xkr   1/1     Running   0          14m
pod/ck-application-client-56cd64698c-4phls           1/1     Running   0          14m
pod/ck-application-mysql-0                           2/2     Running   0          14m
pod/ck-application-server-84c4f67c6-ttn72            1/1     Running   0          14m

NAME                            TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
ck-application-authentication   LoadBalancer   10.106.76.107    localhost     8080/TCP   5s
ck-application-client-http      LoadBalancer   10.97.223.70     localhost     80/TCP     5s
ck-application-client-https     LoadBalancer   10.108.149.254   localhost     443/TCP    5s
ck-application-mysql            ClusterIP      None             <none>        3306/TCP   5s
ck-application-mysql-read       ClusterIP      10.110.144.98    <none>        3306/TCP   5s
ck-application-server           LoadBalancer   10.111.255.161   localhost     5000/TCP   5s

NAME                                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ck-application-authentication   1/1     1            1           14m
deployment.apps/ck-application-client           1/1     1            1           14m
deployment.apps/ck-application-server           1/1     1            1           14m

NAME                                                       DESIRED   CURRENT   READY   AGE
replicaset.apps/ck-application-authentication-6d76dd99b7   1         1         1       14m
replicaset.apps/ck-application-client-56cd64698c           1         1         1       14m
replicaset.apps/ck-application-server-84c4f67c6            1         1         1       14m

NAME                                    READY   AGE
statefulset.apps/ck-application-mysql   1/1     14m
```

The service data will be manage and stored inside Persistent Volume Claim (PVC), in case we need to reploy the service if crashed, all the data will be preserved, and automatically mounted into pod.

9. Wait a bit untill all pods are running
```bash
NAME                                             READY   STATUS    RESTARTS   AGE
ck-application-authentication-6d76dd99b7-c4xkr   1/1     Running   0          11s
ck-application-client-56cd64698c-4phls           1/1     Running   0          11s
ck-application-mysql-0                           2/2     Running   0          11s
ck-application-server-84c4f67c6-ttn72            1/1     Running   0          11s
```

In the contactless checking system, two server are deploying alongwith one MySQL database for back up and one for primary database, and Web Client. To access into the web for user interface. We need to access into the service.

10. Get the service.
```bash
$ kubectl $NAME get svc
```
This will show all the service to access. Select the Web Client service.
```bash
NAME                            TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
ck-application-authentication   LoadBalancer   10.106.76.107    localhost     8080/TCP   5s
ck-application-client-http      LoadBalancer   10.97.223.70     localhost     80/TCP     5s
ck-application-client-https     LoadBalancer   10.108.149.254   localhost     443/TCP    5s
ck-application-mysql            ClusterIP      None             <none>        3306/TCP   5s
ck-application-mysql-read       ClusterIP      10.110.144.98    <none>        3306/TCP   5s
ck-application-server           LoadBalancer   10.111.255.161   localhost     5000/TCP   5s
```
Access https://127.0.0.1 or https://localhost to navigate the Web Client. If access, it will navigate to login page. All the cluster using TLS certificates to authenticate all resources.
![Login](screenshot/Login-page.png)

Enter the Username/Password. By default the API Server created default Admin account. Use the credentials to login into pages.

The homepage will display all analytics metrics and record all check-in times, with the ability to filter by date.
```bash
credentials: Admin/Admin@123
```
![Home-page](https://github.com/user-attachments/assets/0deed286-6628-466a-a623-5577ceba7340)

First, create a set of registered customers in the system. Capture all images and send them to the backend, where they will be stored in both a local and a remote S3 bucket to prevent data loss in case of a system crash.

![Customer-page](https://github.com/user-attachments/assets/5cb48d2d-2c5a-4826-8a80-d54da67d013c)

We can edit all customer information and create a new image dataset for the check-in system, which will be sent to train the ArcFaceModel. To obtain image data, we can either upload images or capture them using a camera device.

![Customer-page-camera](https://github.com/user-attachments/assets/4cf7462c-f87d-40aa-a749-b025409ddaca)
![Customer-page-camera-2](https://github.com/user-attachments/assets/e9d9be0b-d63c-49d0-9b69-e9a906014966)

The collected images will be trained using Jenkins CI. Enter the appropriate parameters and trigger the Jenkins pipeline to train the model with the collected datasets. update

![Jenkins-web-page](https://github.com/user-attachments/assets/dc88da78-3112-45ff-8732-164bc86c9033)
![Jenkins-jobs](https://github.com/user-attachments/assets/afa145f6-4daa-4f1d-9fdf-0bf3490f4b58)

The trained model will be used to detect customer images. On the detection page, a snapshot of the customer's image will be sent to the model server for analysis, and the results will be returned to the client.

![Detection-page](https://github.com/user-attachments/assets/6b3d5317-d745-4ce8-bfca-8accdc5597c8)
