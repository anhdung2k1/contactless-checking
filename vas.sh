#! /bin/bash
##
## vas.sh
##--------

# Directory
test -n "$VAS_GIT" || export VAS_GIT=$(pwd -P)
test -n "$BUILD_DIR" || export BUILD_DIR="$VAS_GIT/build"
test -n "$DATASET_DIR" || export DATASET_DIR="$BUILD_DIR/dataset"
test -n "$MODEL_DIR" || export MODEL_DIR="$BUILD_DIR/yolo_model"
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

# Select options
option=$1
#Get the release commit
git_commit=$(git --git-dir="$VAS_GIT/.git" rev-parse --short=7 HEAD)
change_id=$(git show $git_commit | grep '^\ *Change-Id' | awk '{print $2}')
release=$git_commit

# Dataset for Face Detection
DATASET="https://universe.roboflow.com/ds/EdI7sE1lHX?key=zHmiijqhOV"

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

init() {
    dir_ests
    get_train_dataset
}

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

build_all() {
    buildenv
    build_repo
}

get_version() {
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

    case $__name in
    "authentication")
        pushd .
        cd $API_DIR
        echo "Start to build Spring boot compile"
        docker run -it --rm -v "$(pwd -P)":/app -w /app $MAVEN_IMAGE mvn clean install -Dskiptest \
		    || die "[ERROR]: Failed to compile"
        echo "Copy target file to docker dir"
        cp -f $API_DIR/target/*.jar $DOCKER_DIR/$__name/ \
            || die "Target file does not exists in $API_DIR/target/"
        popd
    ;;
    *)
        echo "Copy folder $__name to docker"
        cp -rf $VAS_GIT/$__name/ $DOCKER_DIR/$__name \
            || die "Source directory does not exists $VAS_GIT/$__name"
        if [[ $__name == "client-server" ]]; then
            cp -f $VAS_GIT/requirements.txt $DOCKER_DIR/$__name \
                || die "Requirements file doest not exists"
        fi
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

    ## Clean target file if exists before build image
    rm -rf $DOCKER_DIR/$__name/*.jar

    version=$(get_version)
    docker build $VAS_GIT/docker/$__name \
            --file $VAS_GIT/docker/$__name/Dockerfile \
            --tag "$DOCKER_REGISTRY/$image_name:$version" \
            --build-arg COMMIT=$git_commit \
            --build-arg APP_VERSION=$version \
            --build-arg BUILD_TIME=`date +"%d/%m/%Y:%H:%M:%S"` \
        || die "Failed to build docker images: $__name"
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
