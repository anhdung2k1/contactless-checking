# Makefile

RELEASE := $(RELEASE)
USERNAME := $(USER)
TOP_DIR := $(CURDIR)
version := $(shell $(TOP_DIR)/vas.sh get_version)

# Clean the repository
clean:
	@echo "Clean Repository"
	./vas.sh clean

# Init the repository
init:
	@echo "Create build dataset and model directory"
	$(TOP_DIR)/vas.sh dir_est
	@echo "mkdir variables folder"
	mkdir -p build/var
	@if [ "$(RELEASE)" = "true" ]; then \
		echo "Generate release version"; \
		$(TOP_DIR)/vas.sh get_version > build/var/.release_version; \
	else \
		echo "Get version prefix"; \
		$(TOP_DIR)/vas.sh get_version > build/var/.version; \
	fi

lint: package-helm lint-helm-tests

lint-helm-tests:
	@echo "Running helm-tests..."
	$(TOP_DIR)/test/helm-validation/helm-tests.py \
		--helmdir $(TOP_DIR)/build/helm-build/ck-application/ck-application

#Build process 
build: 	package-helm \
		build-authentication \
		build-face-client \
       	build-face-model

## Package the helm chart
package-helm:
	@echo "Package helm"
	$(TOP_DIR)/vas.sh build_helm \
		--release=$(RELEASE)
		--user=$(USERNAME)
build-authentication:
	@echo "build authentication Repository"
	$(TOP_DIR)/vas.sh build_repo --name=authentication
build-face-client:
	@echo "build face-client for web service"
	$(TOP_DIR)/vas.sh build_repo --name=face_client

build-face-model:
	@echo "build face-model"
	$(TOP_DIR)/vas.sh build_repo --name=face_model


## Train dataset
train:
	@echo "Create training dataset"
	$(TOP_DIR)/vas.sh get_train_dataset
	## Training the YOLO dataset
	@echo "training dataset"
	$(TOP_DIR)/vas.sh train_dataset

image: 	image-authentication \
		image-face-client \
		image-face-model

image-authentication:
	@echo "build authentication Image"
	$(TOP_DIR)/vas.sh build_image --name=authentication
image-face-client:
	@echo "build face_client Image"
	$(TOP_DIR)/vas.sh build_image --name=face_client
image-face-model:
	@echo "build face_model Image"
	$(TOP_DIR)/vas.sh build_image --name=face_model


push: 	push-authentication \
		push-face-client \
		push-face-model \
		push-helm

push-authentication:
	@echo "push image-authentication"
	$(TOP_DIR)/vas.sh push_image --name=authentication
push-face-client:
	@echo "push image-face-client"
	$(TOP_DIR)/vas.sh push_image --name=face_client
push-face-model:
	@echo "push image-face-model"
	$(TOP_DIR)/vas.sh push_image --name=face_model
push-helm:
	@echo "push helm chart"
	$(TOP_DIR)/vas.sh push_helm

test: 	test-authentication \
		test-face-client \
		test-face-model

test-authentication:
	@echo "test-authentication"
	$(TOP_DIR)/vas.sh test_repo --name=authentication
test-face-model:
	@echo "test-face-model"
	$(TOP_DIR)/vas.sh test_repo --name=face_model
test-face-client:
	@echo "test-face-client"
	$(TOP_DIR)/vas.sh test_repo --name=face_client
test-mysql:
	@echo "test-mysql"
	$(TOP_DIR)/vas.sh test_repo --name=mysql

remove: remove-face-client \
		remove-face-model \
		remove-authentication

remove-face-client:
	@echo "Remove docker client image"
	docker rmi $(DOCKER_REGISTRY)/ck-face_client:$(version) || echo "Image does not exist: $(DOCKER_REGISTRY)/ck-face_client:$(version)"

remove-face-model:
	@echo "Remove docker server image"
	docker rmi $(DOCKER_REGISTRY)/ck-face_server:$(version) || echo "Image does not exist: $(DOCKER_REGISTRY)/ck-face_model:$(version)"

remove-authentication:
	@echo "Remove docker authentication image"
	docker rmi $(DOCKER_REGISTRY)/ck-authentication:$(version) || echo "Image does not exist: $(DOCKER_REGISTRY)/ck-authentication:$(version)"

generate-ca:
	@echo "Generate CA files"
	./vas.sh generate_ca