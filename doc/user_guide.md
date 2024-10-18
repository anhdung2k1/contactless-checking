<!--Document Information:
Prepared: Dung Anh Tran
Document Name: User Guide
Revision: PA1
Date: 2024-10-17
--->

# Contactless Checking (CK) Server User Guide

## Table of Contents

1. [Overview](#overview)  
2. [Description of the Service](#description-of-the-service)  
3. [Main Concepts](#main-concepts)  
   - [Microservices](#microservices)  
   - [Scalability](#scalability)  
   - [Loosely Coupled Services](#loosely-coupled-services)  
   - [Singleton Design Pattern](#singleton-design-pattern)  
   - [Platform as a Service (PaaS)](#platform-as-a-service-paas)  
   - [RESTful API Endpoints](#restful-api-endpoints)  
   - [Biometric Identification](#biometric-identification)  
4. [Architecture](#architecture)  
   - [Logical Interfaces](#logical-interfaces)  
5. [Deployment View](#deployment-view)  
6. [Spring Boot Server Context](#spring-boot-server-context)  
   - [JWT Authentication](#jwt-authentication)  
   - [How JWT Authentication Works](#how-jwt-authentication-works)  
   - [CORS Policy](#cors-policy)  
   - [API Endpoints](#api-endpoints)  
   - [Database Integration](#database-integration)  
   - [Concurrency and Multithreading](#concurrency-and-multithreading)  
   - [Web Socket](#web-socket)  
7. [Flask AI Model Server](#flask-ai-model-server)  
   - [YOLO (You Only Look Once)](#yolo-you-only-look-once)  
   - [FaceNet](#facenet)  
   - [ArcFace](#arcface)  

## Overview

This document provides an overview of the Contactless Checking (CK) Server Service. It gives a brief description of its main feature and its interfaces.

## Description of the Service

CK Server is built on microservices architecture, which is obey loosely-coupling and singleton design rules. Scalable capability since the service handle its own feature.

The CK Service implements CK Server for PaaS environments. CK Server provides two server services (Spring Boot and Flask frameworks) as two main back end for providing API endpoints that give capabilities for client application use to communicate with two server endpoints.

The CK Service use camera gadget and other biologies devices to capture customer's identities who are registered to the system. The service uses client as an admin dashboard system to manage the customer's datasets with two primary servers to process the request from client.

In order to handle multiple users simultaneously, CK Service implements concurrency for dividing multiple threadings in order to split tasks based on user requests.

The main use cases for CK Server are:

* Attendance Check in
* Face Verification and Authentication Service
* Manage Customer registered service
* Security System Management

### Main Concepts

* **Microservices**

    An architectural style used in software development where an application is built as a collection of small, loosely coupled, and independently deployable services. Each service in a microservices architecture is designed to perform a specific business function and can be developed, deployed, and scaled independently of other services.

* **Scalability**
    
    The system scales individual services based on demand, ensuring efficient resource usage.

* **Loosely Coupled Services**

    The services within CK Server are loosely coupled, meaning each service operates independently. This reduces interdependencies between components, making the system more resilient to failures in one service while allowing others to continue functioning smoothly.

* **Singleton Design Pattern**

    Singleton is used for shared components, ensuring only one instance per critical resource.

* **Platform as a Service (PaaS)**

    CK Server is optimized for PaaS environments, allowing seamless cloud deployment and scaling.

* **RESTful API Endpoints**

    The service exposes API endpoints for client interaction with Spring Boot and Flask backends.

* **Biometric Identification**

    CK Server integrates biometric devices like cameras to capture and verify customer identities.

### Architecture

The following picture shows the CK Server service and its architectural context.

![CK-User_diagram](https://github.com/user-attachments/assets/de5f890e-7418-47a2-ab97-8bc8fedac1fa)

Figure 1 Architecture view of CK Server

*Logical Interfaces*
| Interface Logical Name | Interface Realization | Description |
|---|---|---|
| MYSQL.CONFIG | MySQL Database Configurations supports backup and main DB | Xtrabackup and mysql configs ensure DB resilient and prevent data loss |
| CK.SECRETS | Interface used by a service to inject TLS secrets, Opaque secrets | Multiples Secrets are used to secure and prevent secrets being exposed |
| CK.JENKINS | Interface used Jenkins config to train model | Jenkins job CI for training model from remote and local customer dataset |
| CK.PVC | Interface to configure Persistent Volume Claim to store data persistently | Use to persist data in case pod in case pod is crashed |
| CK.LOG.FILE | Interface to transform logging | Transform logging to readable and easily to debug |
| CK.INTERACT | Interface to interact with service | Connect the client service via Ingress or LoadBalancer |
| K8S.CLUSTER | Interface to fetch info from K8S API Server | Fetching information to find services to scrape |
| K8S.API | Interface used K8S API to control K8S Resources | Using Kubectl to control over the K8S Resources |
| AWS.S3 | Interface used S3 Bucket Resources | Using Object Storages Management to remote storage customer datasets and best model trained |

### Deployment View

Contactless Checking (CK) Server is packaged as Docker container. It supports deployment in [Kubernetes](https://kubernetes.io/) using [Helm](https://helm.sh/).

![Deployment Overview](https://github.com/user-attachments/assets/f61d40f1-d625-4b85-a03b-cd65c1d1edf4)

Figure 2 Deployment view of Contactless Checking Server

CK Server is dependent on [Vault](https://www.vaultproject.io/) (not shown in picture).

TLS is enabled by default in CK Server. This means [Vault](https://www.vaultproject.io/) must be installed.

Vault acts as Key Management which can be used to sign own CA (Certificate Authority) and generates TLS keys based on CA has been signed. This means can be configuered TTL (Time-To-Live) and auto renew certificates whenever its nearly expire.

### Spring Boot Server Context

This section delves into the APIs and Security Context of Spring Boot server.

#### JWT Authentication

To secure APIs communication between application, JWT Token is used between the CK Server and client applications. JWT provides a token-based mechanism that ensures secure and stateless authentication for each user request without the need for storing session data on the server.

#### How JWT Authentication Works

User register or logs in providing valid credentials such as username and password.

The server (Spring Boot) in this case verifies these credentials by checking them against stored data in MySQL database.

If the creds are valid, the server generates a JWT token. This token is digitally signed using a secret key know only to server

The JWT provides:

* **Header** Specifies the token type and hashing algorithm (HS256)
```json
  "alg": "HS256",
  "typ": "JWT"
```

* **Payload** Contains claims, which include user information (userID) and token expiration time
```json
  "sub": "1234567890",
  "name": "John Doe",
  "admin": true,
  "iat": 1516239022,
  "exp": 1516242622
```

* **Signature** Secret key is used to create the signature for ensuring data integrity
```scss
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

The token is sent back to the client in response body or header after successfully authentication. The client stores this token usually in session storage (cookies) or local storage

For subsequent requests, the client includes the JWT in the `Authorization` header using `Bearer` scheme

```makefile
Authorization: Bearer <token>
```

### CORS Policy

This to control which domains can access resource hosted on a difference domain (cross-origin requests). By default, browsers block cross-origin requests for security reasons, CORs Policy to allow specific domains to access to Spring Boot resources.

In the context of the `Contactless Checking (CK) Server` which provides API endpoints for a client to interact between client service, setting a proper CORS policy is essential to allow secure cross-origin interactions.

#### Preflight Request

For certain `HTTP/HTTPS` methods (POST, PUT, DELETE, GET, PATCH), browsers first send an OPTIONS request (preflight request) to check if the server allows cross-origin requests.

#### Response Headers

CORS policy in CK Server is enabled by default, includes CORS headers in its response to allow specific domains to access the server's resource

#### Blocked Requests

If the CORS headers are not present or do not allow the requesting domain, the client will block the request

#### API Endpoints

The Spring Boot server exposes `RESTful API endpoints` that the client interacts with. These APIs handle various operations includes:

* Customer check-ins
* Face Verification
* Customer Management
* Attendance Tracking

#### Database Integration

The CK Server is connected to a MySQL database to store and manage customer data, check-in records, and system logs.

It uses Spring Data JPA to interact with the database and ensure smooth data persistence

The database configuration as referenced in `MYSQL.CONFIG` supports both backup and recovery mechanisms tools like `Xtrabackup`, ensuring data resilience and security.

#### Concurrency and Multithreading

The CK server handles multiple user requests concurrently using its underlying `Tomcat` server.

Configureing the thread pool size for handling simultaneous connections to ensure request processing and minimize delays.

Leveraging `asynchronous processing` with `@Async` annotation. This allows non-blocking I/O operations, improving system performance when dealing with long running tasks like batch processing or face recognition.

#### Web Socket

Handling Web Socket connections for real-time features like send notifications to customer after finished validation. The data response to customer need to be fast deliver with TCP/IP connection. This will establish 3-way handshakes for accepting client-server requests.

### Flask AI Model Server

This responsible for handling machine learning tasks related to face detection and recognition. It serves as one of the primary backendsm leveraing deep learning models to perform accurate biometric identification and verification, including `YOLO, FaceNet, and ArcFace`

![Flask API Model Server](https://github.com/user-attachments/assets/e4e640f1-935f-4351-905c-4998ca3f9968)

Figure 3 Flow of Contactless Checking Face Recognition

#### YOLO (You Only Look Once)

This used for real-time object detection, including face detection. It enables the system to quickly identify and locate faces in images or video frames captured by the camera.

In Contactless Checking System, YOLOv8 with ultralystics capable of processing frames at high speeds, making it suitable for real-time applications.

Return the coordinates of the detected faces, which can be used to crop the region of interest for further processing. When users approach the camera for check-in, the YOLO model detects their face in the fram, providing bounding boxes that indicate the location of the detected faces.

#### FaceNet

This model used for face recognition which maps face images to a `128-dimensioanl embedding space`, where similar faces are close to each other, and dissimilar faces are far apart.

FaceNet using `Triplet Loss` distance calculation between embeddings is used to determine the similarity of faces. A small distance indicates a match, while a larger distance suggests a mismatch

This converts the detected faces into numerial vector (embedding) that represents the unique features of the face.

This FaceNet model uses after YOLO model detected a face, the cropped face region is passed to FaceNet to generate face embedding.

The embedding is then compared against a database of registered user's embeddings to verify the user's identity.

#### ArcFace

Arcface can be used alongside FaceNet to further verify a user's identity. When FaceNet generates the face embedding, ArcFace can apply an additional layer of verification using its own face recognition techniques.