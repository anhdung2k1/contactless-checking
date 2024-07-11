#! /bin/bash
##
## vas.sh
##--------

# Directory
test -n "$VAS_GIT" || export VAS_GIT=$(pwd -P)
test -n "$BUILD_DIR" || export BUILD_DIR="$VAS_GIT/build"
test -n "$DATASET_DIR" || export DATASET_DIR="$BUILD_DIR/dataset"

test -n "$MODEL_DIR" || export MODEL_DIR="$BUILD_DIR/yolo_model"
test -n "$ARC_FACE_MODEL_DIR" || export ARC_FACE_MODEL_DIR="$BUILD_DIR/.insightface"
test -n "$API_DIR" || export API_DIR="$VAS_GIT/authentication/authentication"
test -n "$DOCKER_DIR" || export DOCKER_DIR="$VAS_GIT/docker"
test -n "$DOCKER_REGISTRY" || export DOCKER_REGISTRY="anhdung12399"

# Prequiste compiler
test -n "$PYTHON_VERSION" || export PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+\.\d+' | awk -F '.' '{print $2}')
test -n "$MAVEN_IMAGE" || export MAVEN_IMAGE="maven:latest"
# Hyper parameters
test -n "$TASK_TYPE" || export TASK_TYPE=detect #DEFAULT task=detect is one of [detect, segment, classify]
test -n "$MODE_TYPE" || export MODE_TYPE=train #DEFAULT mode=train is one of [train, val, predict, export, track]
test -n "$EPOCHS" || export EPOCHS=50 #DEFAULT EPOCHS=50
test -n "$DEFAULT_MODEL" || export DEFAULT_MODEL="yolov8n.pt" #DEFAULT we get the pretrained model for training process
test -n "$IMAGE_SIZE" || export IMAGE_SIZE=640

prg=$(basename $0) # vas.sh filename
dir=$(dirname $0); dir=$(cd $dir; pwd) #Get root dir
me=$dir/$prg #Get absolutely path vas.sh
vas=$me
#Get the release commit
git_commit=$(git --git-dir="$VAS_GIT/.git" rev-parse --short=7 HEAD)
change_id=$(git show $git_commit | grep '^\ *Change-Id' | awk '{print $2}')
release=$git_commit

# Dataset for Face Detection
DATASET="https://universe.roboflow.com/ds/EdI7sE1lHX?key=zHmiijqhOV"
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
    echo "Create [BUILD,DATASET,MODEL] Folder"
    mkdir "$BUILD_DIR"
    mkdir "$DATASET_DIR"
    mkdir "$MODEL_DIR"
}

get_train_dataset() {
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
    if [[ -d $BUILD_DIR/var/.version ]]; then
    	cat $BUILD_DIR/var/.version
	exit 0
    fi
    suffix=$(git rev-parse HEAD | sed 's/^0*//g' | cut -c1-7 | tr 'a-f' '1-6')
    suffix+=$(git diff --quiet && git diff --cached --quiet || echo '9999')
    echo "$(<$VAS_GIT/VERSION_PREFIX)-${suffix}"
}

## buildenv
##  Set up the build environment
buildenv() {
    test -n "$VAS_GIT" || die "Not set [VAS_GIT]"
    test -n "$PYTHON_VERSION" || die "Python version is not specify"
    
    echo "##################################"
    echo "# Check Python3 version"
    if [[ "$PYTHON_VERSION" -ge 8 ]]; then
        echo "Python3 version available to use: 3.$PYTHON_VERSION"
    else
        echo "Python3 version unavailable to use: 3.$PYTHON_VERSION"
        exit 1
    fi

    echo "##################################"
    echo "# Prepare the build environment: #"
    echo "##################################"
    echo "# Pip install the requirement packages"
    pip install --upgrade pip
    pip install -r requirements.txt
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
        
        mysql_container=$(docker ps --format "{{.Names}}" | grep -i mysql_container)
        if [[ -n "$mysql_container" ]]; then
            docker rm -f $mysql_container
        fi
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
                    $MAVEN_IMAGE mvn clean install -Dskiptest \
		            || die "[ERROR]: Failed to compile"
        echo "Copy target file to docker dir"
        cp -f $API_DIR/target/*.jar $DOCKER_DIR/$__name/ \
            || die "Target file does not exists in $API_DIR/target/"
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
            cp -rf $BUILD_DIR $DOCKER_DIR/$__name \
            || die "Unable to copy the $BUILD_DIR"
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
    docker rmi -f $image_name:$version
    docker build $VAS_GIT/docker/$__name \
            --file $VAS_GIT/docker/$__name/Dockerfile \
            --tag "$DOCKER_REGISTRY/$image_name:$version" \
            --build-arg COMMIT=$git_commit \
            --build-arg APP_VERSION=$version \
            --build-arg BUILD_TIME=`date +"%d/%m/%Y:%H:%M:%S"` \
        || die "Failed to build docker images: $__name"
    
    ## Clean target file if exists
    if [[ $__name == "authentication" ]]; then
        rm -rf $DOCKER_DIR/$__name/*.jar
    else
        rm -rf $DOCKER_DIR/$__name/$__name
        rm -f $DOCKER_DIR/$__name/requirements.txt
    fi
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

## Train the dataset
train_dataset() {
    test -n "$DATASET_DIR" || die "DATASET folder does not exists"
    test -n "$MODEL_DIR" || die "YOLO model folder doest not exists"
    # Push the current dir to stack
    pushd .
    # Saved the model in dir
    cd $MODEL_DIR
    #### Example usage ####
    # yolo task=detect mode=train model=yolov8n.pt data=data/mydataset.yaml epochs=50 imgsz=640
    #######################
    
    #Override the data.yaml file
    echo "train: $DATASET_DIR/train/images" > $DATASET_DIR/data.yaml
    echo "val: $DATASET_DIR/train/images" >> $DATASET_DIR/data.yaml
    echo "test: $DATASET_DIR/test/images" >> $DATASET_DIR/data.yaml
    echo "nc: 1" >> $DATASET_DIR/data.yaml
    echo "names: ['face']" >> $DATASET_DIR/data.yaml

    MODEL_BUILD_DIR="runs/detect/train/weights"
    if [[ -f "$MODEL_DIR/$MODEL_BUILD_DIR/best.pt" ]]; then
    	DEFAULT_MODEL="$MODEL_DIR/$MODEL_BUILD_DIR/best.pt"
    fi

    yolo task=$TASK_TYPE \
         mode=$MODE_TYPE \
         model=$DEFAULT_MODEL \
         data=$DATASET_DIR/data.yaml \
         epochs=$EPOCHS \
         imgsz=$IMAGE_SIZE
    popd
}

wsl_test() {
    test -n "$VAS_GIT" || die "Not set [VAS_GIT]"
    COMMON_DB="checking"
    # This for test in Windows compiler -> expose the ip address of the WSL
    wsl_ip=$(ip addr show eth0 | grep -oP 'inet \K[\d.]+')
    chmod +x $VAS_GIT/test/application.properties
    cp -f $VAS_GIT/test/application.properties $API_DIR/src/main/resources/application.properties

    sed -i -e "s/REPLACE_WITH_DB_IP/${wsl_ip}/g" $API_DIR/src/main/resources/application.properties
    sed -i -e "s/REPLACE_WITH_DB_COMMON/${COMMON_DB}/g" $API_DIR/src/main/resources/application.properties
}

## image_testcon
# Build docker image from Dockerfile for testcon
##
image_testcon() {
    version="1.0.0"
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
    local version="1.0.0"
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
        mysql_container=$(docker ps --format "{{.Names}}" | grep -i mysql_container)
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

        authentication_container=$(docker ps --format "{{.Names}}" | grep -i $__name)
        if [[ -n "$authentication_container" ]]; then
            docker rm -f $__name
        fi

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
        AWS_ACCESS_KEY_ID=$(echo $AWS_ACCESS_KEY_ID)
        AWS_SECRET_ACCESS_KEY=$(echo $AWS_SECRET_ACCESS_KEY)
        test -n $AWS_ACCESS_KEY_ID || die "ENV AWS_ACCESS_KEY_ID required"
        test -n $AWS_SECRET_ACCESS_KEY || die "ENV AWS_SECRET_ACCESS_KEY required"

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
