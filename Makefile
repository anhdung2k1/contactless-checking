# Makefile

RELEASE := $(RELEASE)
USERNAME := $(USER)

# Clean the repository
clean:
	@echo "Clean Repository"
	./vas.sh clean

# Init the repository
init:
	@echo "mkdir variables folder"
	mkdir -p build/var
	@echo "Get version"
	./vas.sh get_version | tee build/var/.version
	@echo "Create build dataset and model directory"
	./vas.sh dir_est
	@echo "Create training dataset"
	./vas.sh get_train_dataset
	@echo "Generate release version"
	@if [ "$(RELEASE)" = "true" ]; then \
		./vas.sh get_version | tee build/var/.release_version; \
	fi

#Build process 
build: 	package-helm \
		build-authentication \
		build-face-client \
       	build-face-model	

## Package the helm chart
package-helm:
	@echo "Package helm"
	./vas.sh build_helm \
		--release=${RELEASE}
		--user=${USERNAME}
build-authentication:
	@echo "build authentication Repository"
	./vas.sh build_repo --name=authentication
build-face-client:
	@echo "build face-client for web service"
	./vas.sh build_repo --name=face_client

build-face-model:
	@echo "build face-model"
	./vas.sh build_repo --name=face_model


## Train dataset
train:
	## Training the YOLO dataset
	@echo "training dataset"
	./vas.sh train_dataset

image: 	image-authentication \
		image-face-client \
		image-face-model

image-authentication:
	@echo "build authentication Image"
	./vas.sh build_image --name=authentication
image-face-client:
	@echo "build face_client Image"
	./vas.sh build_image --name=face_client
image-face-model:
	@echo "build face_model Image"
	./vas.sh build_image --name=face_model


push: 	push-authentication \
		push-face-client \
		push-face-model

push-authentication:
	@echo "push image-authentication"
	./vas.sh push_image --name=authentication
push-face-client:
	@echo "push image-face-client"
	./vas.sh push_image --name=face_client
push-face-model:
	@echo "push image-face-model"
	./vas.sh push_image --name=face_model

