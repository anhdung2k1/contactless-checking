# Set default variables
_TESTCON_IMAGE ?= "anhdung12399/testcon:1.1.0"
_TESTCON_RUN ?= $(shell docker run -it --rm -v ${PWD}:${PWD} -w ${PWD} ${_TESTCON_IMAGE})

RELEASE ?= false
USERNAME ?= $(USER)

# Phony targets to avoid conflicts with files
.PHONY: clean init build package-helm build-authentication build-face-client build-face-model train \
        image image-authentication image-face-client image-face-model push push-authentication \
        push-face-client push-face-model test test-authentication test-face-client test-face-model \
        get_lfw_dataset

# Clean the repository
clean:
	@echo "Cleaning repository"
	./vas.sh clean

# Init the repository
init:
	@echo "Creating build dataset and model directory"
	./vas.sh dir_est
	@echo "Creating variables folder"
	mkdir -p build/var
	@echo "Creating training dataset"
	./vas.sh get_train_dataset
	@if [ "$(RELEASE)" = "true" ]; then \
		echo "Generating release version"; \
		./vas.sh get_version > build/var/.release_version; \
	else \
		echo "Getting version prefix"; \
		./vas.sh get_version > build/var/.version; \
	fi

# Build process 
build: package-helm build-authentication build-face-client build-face-model

## Package the helm chart
package-helm:
	@echo "Packaging Helm chart"
	./vas.sh build_helm --release=$(RELEASE) --user=$(USERNAME)

## Build individual components
build-authentication:
	@echo "Building authentication repository"
	./vas.sh build_repo --name=authentication

build-face-client:
	@echo "Building face-client for web service"
	./vas.sh build_repo --name=face_client

build-face-model:
	@echo "Building face-model"
	./vas.sh build_repo --name=face_model

# Train the dataset
train:
	@echo "Training dataset"
	docker run -it --rm -v ${PWD}:${PWD} -w ${PWD} ${_TESTCON_IMAGE} bash -c "which yolo && yolo version && ${PWD}/vas.sh train_dataset"
# Build Docker images for each component
image: image-authentication image-face-client image-face-model

image-authentication:
	@echo "Building authentication Docker image"
	./vas.sh build_image --name=authentication

image-face-client:
	@echo "Building face-client Docker image"
	./vas.sh build_image --name=face_client

image-face-model:
	@echo "Building face-model Docker image"
	./vas.sh build_image --name=face_model

# Push Docker images to the registry
push: push-authentication push-face-client push-face-model

push-authentication:
	@echo "Pushing authentication image"
	./vas.sh push_image --name=authentication

push-face-client:
	@echo "Pushing face-client image"
	./vas.sh push_image --name=face_client

push-face-model:
	@echo "Pushing face-model image"
	./vas.sh push_image --name=face_model

# Run tests for each component
test: test-authentication test-face-client test-face-model

test-authentication:
	@echo "Testing authentication"
	./vas.sh test_repo --name=authentication

test-face-client:
	@echo "Testing face-client"
	./vas.sh test_repo --name=face_client

test-face-model:
	@echo "Testing face-model"
	./vas.sh test_repo --name=face_model

# Additional tasks
get_lfw_dataset:
	@echo "Creating LFW dataset"
	./vas.sh get_lfw_dataset
