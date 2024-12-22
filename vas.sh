#! /bin/bash
##
## vas.sh
##--------

# Directory
test -n "$VAS_GIT" || export VAS_GIT=$(pwd -P)
test -n "$TEST_DIR" || export TEST_DIR="$VAS_GIT/test"
test -n "$BUILD_DIR" || export BUILD_DIR="$VAS_GIT/build"
test -n "$HELM_DIR" || export HELM_DIR="$BUILD_DIR/helm-build/ck-application"
test -n "$DATASET_DIR" || export DATASET_DIR="$BUILD_DIR/dataset"
test -n "$RELEASE" || export RELEASE=false
test -n "$MODEL_DIR" || export MODEL_DIR="$BUILD_DIR/yolo_model"
test -n "$ARC_FACE_MODEL_DIR" || export ARC_FACE_MODEL_DIR="$BUILD_DIR/.insightface"
test -n "$API_DIR" || export API_DIR="$VAS_GIT/authentication/authentication"
test -n "$DOCKER_DIR" || export DOCKER_DIR="$VAS_GIT/docker"
test -n "$INT_HELM_DIR" || export INT_HELM_DIR="$VAS_GIT/helm/ck-application-integration-chart"
test -n "$DOCKER_REGISTRY" || export DOCKER_REGISTRY="anhdung12399"

# Prequiste compiler
test -n "$MAVEN_IMAGE" || export MAVEN_IMAGE="maven:latest"
# Hyper parameters
test -n "$TASK_TYPE" || export TASK_TYPE=detect #DEFAULT task=detect is one of [detect, segment, classify]
test -n "$MODE_TYPE" || export MODE_TYPE=train #DEFAULT mode=train is one of [train, val, predict, export, track]
test -n "$EPOCHS" || export EPOCHS=100 #DEFAULT EPOCHS=50
test -n "$DEFAULT_MODEL" || export DEFAULT_MODEL="yolo11m.pt" #DEFAULT we get the pretrained model for training process
test -n "$IMAGE_SIZE" || export IMAGE_SIZE=640
test -n "$BATCH_SIZE" || export BATCH_SIZE=8
test -n "$SAVE_PATH" || export SAVE_PATH=$MODEL_DIR
test -n "$AMP" || export AMP=false

prg=$(basename $0) # vas.sh filename
dir=$(dirname $0); dir=$(cd $dir; pwd) #Get root dir
me=$dir/$prg #Get absolutely path vas.sh
vas=$me
#Get the release commit
git_commit=$(git --git-dir="$VAS_GIT/.git" rev-parse --short=7 HEAD)
change_id=$(git show $git_commit | grep '^\ *Change-Id' | awk '{print $2}')
release=$git_commit

# Dataset for Face Detection
DATASET="https://universe.roboflow.com/ds/lXdnWfLr4T?key=dSif05B23L"
MODEL_URL="https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"

clean() {
    echo "Remove build directory..."
    rm -rf "$VAS_GIT/build"
    echo "Remove sucessfully"
}

die() {
    echo "ERROR: $1" >&2
    exit 1
}

help() {
    grep '^##' $0 | cut -c3-
    exit 0
}

test -n "$1" || help
echo "$1" | grep -qi "^help\|-h" && help

dir_est() {
    echo "Creating [BUILD, DATASET, MODEL] directories if they do not exist..."

    # Check and create BUILD_DIR if it does not exist
    if [ ! -d "$BUILD_DIR" ]; then
        echo "Creating $BUILD_DIR..."
        mkdir -p "$BUILD_DIR"
    else
        echo "$BUILD_DIR already exists. Skipping creation."
    fi

    # Check and create MODEL_DIR if it does not exist
    if [ ! -d "$MODEL_DIR" ]; then
        echo "Creating $MODEL_DIR..."
        mkdir -p "$MODEL_DIR"
    else
        echo "$MODEL_DIR already exists. Skipping creation."
    fi

    echo "Directory setup complete."
}

# Get Roflow Dataset for training YOLO
get_train_dataset() {
    test -n "$DATASET_DIR" || die "DATASET_DIR must be created"
    # Check and create DATASET_DIR if it does not exist
    if [ ! -d "$DATASET_DIR" ]; then
        echo "Creating $DATASET_DIR..."
        mkdir -p "$DATASET_DIR"
    else
        echo "$DATASET_DIR already exists. Skipping creation."
    fi

    if [[ -d "$DATASET_DIR" && -z $(ls -A $DATASET_DIR) ]]; then
        echo "Roboflow zip file"
        curl -L $DATASET > "$DATASET_DIR/roboflow.zip"
        # Push the current directory in stack
        pushd .
        cd $DATASET_DIR
        # Unzip the dataset and remove zip file
        unzip $DATASET_DIR/roboflow.zip && rm -rf $DATASET_DIR/roboflow.zip
        # Go back to previous directory
        popd
    else
        echo "Dataset directory is not empty"
    fi
}

get_arc_face_model() {
    test $ARC_FACE_MODEL_DIR | mkdir -p "$ARC_FACE_MODEL_DIR"
    if [[ -d "$ARC_FACE_MODEL_DIR" && -z $(ls -A $ARC_FACE_MODEL_DIR) ]]; then
        echo "ARC_FACE model untar"
        curl -L $MODEL_URL > "$ARC_FACE_MODEL_DIR/buffalo_l.zip"
        pushd .
        cd $ARC_FACE_MODEL_DIR
        # Unzip the model and remove zip file
        unzip $ARC_FACE_MODEL_DIR/buffalo_l.zip && rm -rf $ARC_FACE_MODEL_DIR/buffalo_l.zip
        # Go back to previous directory
        popd
    else
        echo "ARC_FACE model directory is not empty"
    fi
}

build_all() {
    buildenv
    build_repo
}

get_version() {
    test -n "$BUILD/var" || mkdir $BUILD/var
    if [[ "$RELEASE" = true ]]; then
        if [[ -s $BUILD_DIR/var/.release_version ]]; then
            cat $BUILD_DIR/var/.release_version
            exit 0
        fi
        release_version=$(git tag | sort -V | tail -1)
        echo "${release_version}"
    else
        if [[ -s $BUILD_DIR/var/.version ]]; then
            cat $BUILD_DIR/var/.version
            exit 0
        fi
        suffix=$(git rev-parse HEAD | sed 's/^0*//g' | cut -c1-7 | tr 'a-f' '1-6')
        suffix+=$(git diff --quiet && git diff --cached --quiet || echo '9999')
        echo "$(<$VAS_GIT/VERSION_PREFIX)-${suffix}"
    fi
}

get_user_id() {
    local_container=$1
    local hash=$(sha256sum <<< "${container}" | cut -f1 -d ' ')
    bc -q <<< "scale=0;obase=10;ibase=16;(${hash^^}%30D41)+186A0"
}

# Copy CA file to integration charts
generate_ca() {
    test -n "$INT_HELM_DIR" || die "Module [INT_HELM_DIR] not set"
    test -n "$TEST_DIR" || die "Module [TEST_DIR] not set"

    SSL_TEST_DIR="$TEST_DIR/ssl"
    HELM_TEMPLATE_FILE_DIR="$INT_HELM_DIR/files"
    gen_ca_path="$TEST_DIR/generate_ca.sh"
    key_file="ca.key"
    cert_file="ca.crt"

    echo "############### Generating Ceritificate Authority ############"
    echo "Go to $TEST_DIR"
    pushd .
    cd $TEST_DIR
    $gen_ca_path

    # Check if HELM_TEMPLATE_FILE_DIR exists, if not, create the directory
    if [ ! -d "$HELM_TEMPLATE_FILE_DIR" ]; then
        echo "Creating directory $HELM_TEMPLATE_FILE_DIR"
        mkdir -p "$HELM_TEMPLATE_FILE_DIR" \
            || die "Failed to create directory $HELM_TEMPLATE_FILE_DIR"
    fi

    echo "############### Certificates ############"
    # Copy ca key file
    cp -f "$SSL_TEST_DIR/$key_file" "$HELM_TEMPLATE_FILE_DIR/$key_file" \
        || die "Failed to copy $SSL_TEST_DIR/$key_file to $HELM_TEMPLATE_FILE_DIR/$key_file"
    echo "Copy $cert_file file from $SSL_TEST_DIR/$cert_file to $HELM_TEMPLATE_FILE_DIR/$cert_file"
    # Copy ca cert file
    cp -f "$SSL_TEST_DIR/$cert_file" "$HELM_TEMPLATE_FILE_DIR/$cert_file" \
        || die "Failed to copy $SSL_TEST_DIR/$cert_file to $HELM_TEMPLATE_FILE_DIR/$cert_file"s
    popd
}

## Build Spring boot *.tar and socket binary
build_repo() {
    test -n "$API_DIR" || die "Not set [API_DIR]"
    test -n "$MAVEN_IMAGE" || die "Not set image [MAVEN_IMAGE]"
    test -n "$__name" || die "Module name required"

    echo "##################################"
    echo "# Prepare the build repository : #"
    echo "##################################"

    COMMON_DB="checking"

    case $__name in
    "authentication")
        pushd .
        cd $API_DIR
        echo "Start to build Spring boot compile"
        # To compile the Spring boot, must start the mysql docker for temporaly -> remove after build
        rm -f $API_DIR/src/main/resources/application.properties
        
        docker ps -a | grep -i mysql_container | awk '$1 {print $1}' | xargs docker rm -f
        # Start docker mysql container
        docker run -d --name mysql_container \
            -e MYSQL_ROOT_PASSWORD=root \
            -e MYSQL_DATABASE=$COMMON_DB \
            -e MYSQL_USER=$COMMON_DB \
            -e MYSQL_PASSWORD=$COMMON_DB \
            -p 3306:3306 \
            mysql:latest \
            || die "[ERROR]: Failed to run mysql docker"
        mysql_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql_container)
        echo $mysql_IP
        docker run -it --rm -v "$(pwd -P)":/app \
                    -w /app \
                    -e DB_HOST=$mysql_IP \
                    -e DB_USERNAME=$COMMON_DB \
                    -e DB_NAME=$COMMON_DB \
                    -e DB_PASSWORD=$COMMON_DB \
                    $MAVEN_IMAGE mvn clean install -DskipTests \
		            || die "[ERROR]: Failed to compile"
        echo "Copy target file to docker dir"
        cp -f $API_DIR/target/*.jar $DOCKER_DIR/$__name/ \
            || die "Target file does not exists in $API_DIR/target/"
        cp -f $API_DIR/src/main/resources/application.yaml $DOCKER_DIR/$__name/ \
            || die "application.yaml file does not exists in $API_DIR/src/main/resources"
        # Remove the mysql container
        docker rm -f mysql_container \
            || die "Could not remove mysql container"
        popd
    ;;
    *)
        if [ $__name == "face_model" ]; then
            echo "Copy requirements.txt to $__name"
            cp -f $VAS_GIT/requirements.txt $DOCKER_DIR/$__name \
            || die "Unable to copy the requirements.txt"
        fi

        echo "Copy folder $__name to docker"
        cp -rf $VAS_GIT/$__name/ $DOCKER_DIR/$__name \
            || die "Source directory does not exists $VAS_GIT/$__name"
    ;;
    esac
}

## build_image
## Build docker image from Dockerfile
##
## --name=<module name>
##
build_image() {
    test -n "$VAS_GIT" || die "Not set [VAS_GIT]"
    test -n "$__name" || die "Module name required"
    image_name=ck-$__name

    version=$(get_version)

    #remove the docker images before create new ones
    docker build $VAS_GIT/docker/$__name \
            --file $VAS_GIT/docker/$__name/Dockerfile \
            --tag "$DOCKER_REGISTRY/$image_name:$version" \
            --build-arg COMMIT=$git_commit \
            --build-arg APP_VERSION=$version \
            --build-arg BUILD_TIME=`date +"%d/%m/%Y:%H:%M:%S"` \
        || die "Failed to build docker images: $__name"
}

## save_image
## Save image from local build repository
##
## --name=<module name>
##
save_image() {
    test -n "$VAS_GIT" || die "Not set [VAS_GIT]"
    test -n "$__name" || die "Module name required"
    image_name=ck-$__name

    mkdir -p $BUILD_DIR/images
    cd $BUILD_DIR/images
    version=$(get_version)

    echo "Save image: $image_name"
    rm -rf ${image_name}:$version.tgz && rm -rf ${image_name}:$version.sha256
    docker save $DOCKER_REGISTRY/${image_name}:$version \
            | gzip -vf - > ${image_name}-$version.tgz
    sha256sum "${image_name}-$version.tgz" > "${image_name}-$version.sha256"
    cat "${image_name}-$version.sha256"
}

## create helm_md5sum
## Create the md5sum file for Helm chart
##
create_helm_md5sum() {
    cd $BUILD_DIR/helm-build/ck-application
    version=$(get_version)
    md5sum "ck-application-$version.tgz" > "ck-application-$version.md5sum"
    cat "ck-application-$version.md5sum"
}

## build_helm
## Packages the helm chart for checking application
##
## --release=<true/false>
##
build_helm() {
    test -n "$__release" && export RELEASE=$__release
    test -n "$__user" || __user=$USER

    local version=$(get_version)

    destination="${VAS_GIT}/build/helm-build"
    rm -rf $destination && mkdir $destination
    chart="${VAS_GIT}/helm/ck-application/Chart.yaml"
    ck_chart_name=$(basename $(dirname $chart))
    
    source_tmp="${VAS_GIT}/build/.helm_temp_ws"
    source="$source_tmp/$ck_chart_name"
    rm -rf $source_tmp && mkdir $source_tmp
    if [ ! -d $source ]; then
        cp -r ${VAS_GIT}/helm/$ck_chart_name $source
    fi 

    mkdir -p "$destination/$ck_chart_name"

    sed -i -e "s/^version: .*/version: ${version}/" $source/Chart.yaml
    sed -i -e "s/%%VERSION%%/${version}/" $source/ck-product-info.yaml
    sed -i -e "s/%%REGISTRY%%/${DOCKER_REGISTRY}/" $source/ck-product-info.yaml
    
    helm package $source \
        --dependency-update \
        --destination $destination/$ck_chart_name \
        --version $version \
    || die "Failed to package helm chart"

    ck_chart_path="$destination/$ck_chart_name/$ck_chart_name-$version.tgz"

    #Untar the ck chart
    tar -xvf $ck_chart_path -C "$(dirname $ck_chart_path)"

    create_helm_md5sum
}

## Push image
## Push docker image to Docker Registry
##
## --name=<module name>
##
push_image() {
   test -n "$VAS_GIT" || die "Not set [VAS_GIT]"
   test -n "$__name" || die "Module name required"
   test -n "$DOCKER_REGISTRY" || die "Not set [DOCKER_REGISTRY]"
   image_name=ck-$__name
   version=$(get_version)

   ## Docker push to docker registry
   docker push $DOCKER_REGISTRY/$image_name:$version \
	   || die "Failed to push docker registry: $DOCKER_REGISTRY"
}

## Push helm
## Push helm package to Docker Registry
##
## --name=<module name>
##
push_helm() {
    if [ $RELEASE == true ]; then
        test -n "$VAS_GIT" || die "Not set [VAS_GIT]"
        test -n "$DOCKER_REGISTRY" || die "Not set [DOCKER_REGISTRY]"
        test -n "$HELM_DIR" || die "Not set [HELM_DIR]"
        image_name=ck-$__name
        version=$(get_version)
        registry=oci://registry-1.docker.io

        echo "RELEASE is true. Push helm chart to $registry/$DOCKER_REGISTRY"
        ## Helm push to docker registry
        helm push $HELM_DIR/ck-application-$version.tgz \
                $registry/$DOCKER_REGISTRY \
                || die "Failed to push helm chart to $registry/$DOCKER_REGISTRY"
    else
        echo "RELEASE is false. Skip to push helm chart"
    fi
}

## Train the dataset
train_dataset() {
    test -n "$DATASET_DIR" || die "DATASET folder does not exists"
    test -n "$MODEL_DIR" || die "YOLO model folder doest not exists"
    # Push the current dir to stack
    pushd .
    # Saved the model in dir
    cd $MODEL_DIR
    #### Example usage ####
    # yolo task=detect mode=train model=yolo11n.pt data=data/mydataset.yaml epochs=50 imgsz=640
    #######################

    MODEL_BUILD_DIR="runs/detect/train/weights"
    if [[ -f "$MODEL_DIR/$MODEL_BUILD_DIR/best.pt" ]]; then
    	DEFAULT_MODEL="$MODEL_DIR/$MODEL_BUILD_DIR/best.pt"
    fi

    yolo task=$TASK_TYPE \
         mode=$MODE_TYPE \
         model=$DEFAULT_MODEL \
         data=$DATASET_DIR/data.yaml \
         epochs=$EPOCHS \
         imgsz=$IMAGE_SIZE \
         batch=$BATCH_SIZE \
         save=true \
         project=$SAVE_PATH \
         amp=$AMP
    popd
}

wsl_test() {
    test -n "$VAS_GIT" || die "Not set [VAS_GIT]"
    COMMON_DB="checking"
    # This for test in Windows compiler -> expose the ip address of the WSL
    wsl_ip=$(ip addr show eth0 | grep -oP 'inet \K[\d.]+')
    chmod +x $VAS_GIT/test/application.properties
    cp -f $VAS_GIT/test/application.properties $API_DIR/src/main/resources/application.properties

    sed -i -e "s/@@REPLACE_WITH_DB_IP/${wsl_ip}/g" $API_DIR/src/main/resources/application.properties
    sed -i -e "s/@@REPLACE_WITH_DB_COMMON/${COMMON_DB}/g" $API_DIR/src/main/resources/application.properties

    mysql_container=$(docker ps -a --format "{{.Names}}" | grep -i mysql_container)
    if [[ ! -n "$mysql_container" ]]; then
            # Start docker mysql container
        docker run -d --name mysql_container \
            -e MYSQL_ROOT_PASSWORD=root \
            -e MYSQL_DATABASE=${COMMON_DB} \
            -e MYSQL_USER=${COMMON_DB} \
            -e MYSQL_PASSWORD=${COMMON_DB} \
            -p 3306:3306 \
            mysql:latest \
        || die "[ERROR]: Failed to run mysql docker"
    else
        docker start mysql_container
    fi
}

## image_testcon
# Build docker image from Dockerfile for testcon
##
image_testcon() {
    version="1.1.0"
    name=testcon
    export DOCKER_BUILDKIT=1
    docker build $VAS_GIT/test/$name \
        --no-cache \
        --file $VAS_GIT/test/$name/Dockerfile \
        --tag "${DOCKER_REGISTRY}/$name:$version" \
        || die "Failed to build docker image: $name"
    docker images | grep $name
}

## testcon_up
# Push docker image to docker registry
##
testcon_up() {
    local version="1.1.0"
    name=testcon
    docker push $DOCKER_REGISTRY/$name:$version \
	   || die "Failed to push docker registry: $DOCKER_REGISTRY"
}

## Docker test running on local for building
test_repo() {
    test -n "$VAS_GIT" || die "Not set [VAS_GIT]"
    test -n "$__name" || die "Module name required"
    COMMON_DB="checking"
    image_name=ck-$__name
    version=$(get_version)

    echo "##################################"
    echo "# Prepare the docker local build : #"
    echo "##################################"

    echo "Start to test $__name"

    case $__name in
    "authentication")        
        mysql_container=$(docker ps -a --format "{{.Names}}" | grep -i mysql_container)
        if [[ ! -n "$mysql_container" ]]; then
             # Start docker mysql container
            docker run -d --name mysql_container \
                -e MYSQL_ROOT_PASSWORD=root \
                -e MYSQL_DATABASE=${COMMON_DB} \
                -e MYSQL_USER=${COMMON_DB} \
                -e MYSQL_PASSWORD=${COMMON_DB} \
                -p 3306:3306 \
                mysql:latest \
            || die "[ERROR]: Failed to run mysql docker"
        else
            docker start mysql_container
        fi
       
        mysql_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql_container)
        echo $mysql_IP

        # Remove existing authentication repo
        docker ps -a | grep -i $__name | awk '$1 {print $1}' | xargs docker rm -f

        docker run -it --rm -d --name $__name \
                -e DB_HOST=${mysql_IP} \
                -e DB_USERNAME=${COMMON_DB} \
                -e DB_NAME=${COMMON_DB} \
                -e DB_PASSWORD=${COMMON_DB} \
                -p 8080:8080 \
                ${DOCKER_REGISTRY}/${image_name}:${version} \
                || die "[ERROR]: Failed to run docker $__name"
    ;;
    "face_model")
        face_model_container=$(docker ps --format "{{.Names}}" | grep -i $__name)
        if [[ -n "$face_model_container" ]]; then
            docker rm -f $__name
        fi

        docker run -it --rm -d --name $__name \
                -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
                -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
                -p 5000:5000 \
                ${DOCKER_REGISTRY}/${image_name}:${version} \
                || die "[ERROR]: Failed to run docker $__name"
    ;;
    "face_client")
        face_client_container=$(docker ps --format "{{.Names}}" | grep -i $__name)
        if [[ -n "$face_client_container" ]]; then
            docker rm -f $__name
        fi

        docker run -it --rm -d --name $__name \
                -p 80:80 \
                ${DOCKER_REGISTRY}/${image_name}:${version} \
                || die "[ERROR]: Failed to run docker $__name"
    ;;
    "mysql")
	mysql_container=$(docker ps -a --format "{{.Names}}" | grep -i mysql_container)
        if [[ ! -n "$mysql_container" ]]; then
             # Start docker mysql container
            docker run -d --name mysql_container \
                -e MYSQL_ROOT_PASSWORD=root \
                -e MYSQL_DATABASE=${COMMON_DB} \
                -e MYSQL_USER=${COMMON_DB} \
                -e MYSQL_PASSWORD=${COMMON_DB} \
                -p 3306:3306 \
                mysql:latest \
            || die "[ERROR]: Failed to run mysql docker"
        else
            docker start mysql_container
        fi
       
        mysql_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql_container)
        echo $mysql_IP
    esac
}

#Get the command
cmd=$1
shift
grep -q "^$cmd()" $0 || die "Invalid command [$cmd]"

while echo "$1" | grep -q '^--'; do
    if echo $1 | grep -q =; then
        o=$(echo "$1" | cut -d= -f1 | sed -e 's,-,_,g')
        v=$(echo "$1" | cut -d= -f2-)
        eval "$o=\"$v\""
    else
        o=$(echo "$1" | sed -e 's,-,_,g')
		eval "$o=yes"
    fi
    shift
done
unset o
long_opts=`set | grep '^__' | cut -d= -f1`

#Execute command
trap "die Interrupted" INT TERM
$cmd "$@"
status=$?
exit $status
