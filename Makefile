RELEASE := false
USERNAME := $(USER)

# Clean the repository
clean:
	@echo "Clean Repository"
	./vas.sh clean
# init the repository
init:
	@echo "mkdir variables"
	test -d build/var || mkdir build/var
	@echo "Get version"
	./vas.sh get_version > /build/var/.version
	@echo "Create build dataset and model directory"
	./vas.sh dir_est
	@echo "Create training dataset"
	./vas.sh get_train_dataset
	@echo "Get commit hash"
	git rev-parse --short=7 HEAD > /build/var/.version
	@echo "Generate release version"
	@git tag | grep -v + | sort -V | tail -1 | sed 's/-/+/g' > build/var/.released-version

#Build process 
build: build-env \
	package-helm \
	build-authentication \
	build-socket-server 

build-env:
	@echo "Build Repository"
	./vas.sh buildenv
## Package the helm chart
package-helm:
	@echo "Package helm"
	./vas.sh build_helm \
		--release=${RELEASE}
		--user=${USERNAME}
build-authentication:
	@echo "build authentication Repository"
	./vas.sh build_repo --name=authentication
build-socket-server:
	@echo "build socket-server"
	./vas.sh build_repo --name=socket-server

## Train dataset
train:
	## Training the YOLO dataset
	@echo "training dataset"
	./vas.sh train_dataset

image: image-authentication \
	image-socket-server 

image-authentication:
	@echo "build authentication Image"
	./vas.sh build_image --name=authentication
	./vas.sh save_image --name=authentication
image-socket-server:
	@echo "build socket-server Image"
	./vas.sh build_image --name=socket-server
	./vas.sh save_image --name=socket-server

push: push-authentication \
	push-socket-server 

push-authentication:
	@echo "push image-authentication"
	./vas.sh push_image --name=authentication
push-socket-server:
	@echo "push image-socket-server"
	./vas.sh push_image --name=socket-server

## Docker test local -> this test for local development
test: test-authentication \
	test-socket-server

test-authentication:
	@echo "test image-authentication local build image"
	./vas.sh test_repo --name=authentication
test-socket-server:
	@echo "test image-socket-server local build image"
	./vas.sh test_repo --name=socket-server
