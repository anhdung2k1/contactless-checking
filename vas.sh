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

# Prequiste compiler
test -n "$PYTHON_VERSION" || export PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+\.\d+' | awk -F '.' '{print $2}')
test -n "$JAVA_VERSION" || export JAVA_VERSION=$(java --version | grep -oP '\d+\.\d+\.\d+' -m 1 | awk -F '.' '{print $1}')
test -n "$MAVEN_VERSION" || export MAVEN_VERSION=$(mvn --version | grep -oP '\d+\.\d+\.\d+' -m 1 | awk -F '.' '{print $2}')
# Hyper parameters
test -n "$TASK_TYPE" || export TASK_TYPE=detect #DEFAULT task=detect is one of [detect, segment, classify]
test -n "$MODE_TYPE" || export MODE_TYPE=train #DEFAULT mode=train is one of [train, val, predict, export, track]
test -n "$EPOCHS" || export EPOCHS=10 #DEFAULT EPOCHS=10
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
    echo "ERROR: $*" >&2
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
    test -n "$JAVA_VERSION" || die "Java version is not specify"
    test -n "$MAVEN_VERSION" || die "Maven version is not specify"
    
    echo "##################################"
    echo "# Check Python3 version"
    if [[ "$PYTHON_VERSION" -ge 8 ]]; then
        echo "Python3 version available to use: 3.$PYTHON_VERSION"
    else
        echo "Python3 version unavailable to use: 3.$PYTHON_VERSION"
        exit 1
    fi

    echo "##################################"
    echo "# Check Java and Maven version"
    if [[ "$JAVA_VERSION" -ge 17 ]]; then
        echo "Java version available to use: Java version $JAVA_VERSION"
    else
        echo "Java version unavailable to use: Java version $JAVA_VERSION"
        exit 1
    fi

    if [[ "$MAVEN_VERSION" -ge 9 ]]; then
        echo "Maven version available to use: Maven version $MAVEN_VERSION"
    else
        echo "Maven version unavailable to use: Maven version $MAVEN_VERSION"
        exit 1
    fi

    echo "##################################"
    echo "# Prepare the build environment: #"
    echo "##################################"
    pip install --upgrade pip
    pip install -r requirements.txt
}

## Build Spring boot *.tar and socket binary
build_repo() {
    test -n "$API_DIR" || die "Not set [API_DIR]"

    echo "##################################"
    echo "# Prepare the build repository : #"
    echo "##################################"
    pushd .
    cd $API_DIR
    mvn clean install -Dskiptest
    cp -f $API_DIR/target/*.jar $DOCKER_DIR/api-server
    popd
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

    if [[ -f "$MODEL_DIR/runs/detect/train/weights/best.pt" ]]; then
    	DEFAULT_MODEL="$MODEL_DIR/runs/detect/train/weights/best.pt"
    fi

    yolo task=$TASK_TYPE \
         mode=$MODE_TYPE \
         model=$DEFAULT_MODEL \
         data=$DATASET_DIR/data.yaml \
         epochs=$EPOCHS \
         imgsz=$IMAGE_SIZE
    popd
}

# CLI to get to vas option
case $option in
    "clean") echo "STEP: Clean"
             clean
    ;;
    "init") echo "STEP: Initialize the build process"
            init
    ;;
    "train") echo "STEP: Train with custom dataset"
            train_dataset
    ;;
    "buildenv") echo "STEP: Build environment"
            buildenv
    ;;
    "build_all") echo "STEP: Build all processes"
            build_all
    ;;
    "get_version") get_version
    ;;
    esac

