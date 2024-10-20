#!/usr/bin/env bash

TOP_DIR=$(git rev-parse --show-toplevel)

function die() {
    echo "ERROR: $@"
    popd &>/dev/null
    exit 1
}

function dependency_update() {
    echo "Helm dependency update..."
    helm dependency update . &>/dev/null || die "Failed to update dependencies"
    echo "Done."
}

function replace_with_local_build() {
    echo "Copying local helm chart to integrated chart..."
    pushd $TOP_DIR &>/dev/null

    local version=$($TOP_DIR/vas.sh get_version)
    local build_dir=${TOP_DIR}/build/helm-build/ck-application
    local int_char_dir=${TOP_DIR}/helm/ck-application-integration-chart/charts
    local chart=${build_dir}/ck-application-${version}.tgz

    [[ -f ${chart} ]] || die "The chart ${chart} does not exist! Need to build first..."

    # replace the official with the local build
    rm -f ${int_char_dir}/ck-application-* || die "failed to remove CK App official helm chart"
    cp ${chart} ${int_char_dir} || die "failed to copy local CK App chart to integrated chart"

    popd &>/dev/null
    echo "Done."
}

function cleanup_ns() {
    echo "Cleaning up $namespace..."
    kubectl get ns $namespace &>/dev/null || { kubectl create ns $namespace ; return ; }
    local all_releases=$($h list --short 2>/dev/null )

    if [ ! -z "$all_releases" ]; then
        $h uninstall ${all_releases} &>/dev/null || die "failed to uninstall helm releases"
    fi
    cleanup_resources pvc
    cleanup_resources secret
    echo "Done."
}

function cleanup_resources() {
    for name in $($k get $1 -o jsonpath={.items[*].metadata.name}); do
        $k delete $1 $name;
    done
}

function run_helm_command() {
    local action=$1
    shift
    local bold=$(tput bold)
    local normal=$(tput sgr0)

    if [[ "$action" == "install" ]]; then
        echo "*** Here are the ${bold}helm command to install the integrated helm chart ${normal} ***"; echo
        echo ${bold} $h install ${release_name} . $@ ${normal}; echo
    else
        echo "*** Here are the ${bold}helm command to upgrade the integrated helm chart ${normal} ***"; echo
        echo ${bold} $h upgrade ${release_name} . $@ ${normal}; echo
    fi
    while true; do
        read -p "Ok to go? [y/n] " yn
        echo
        case $yn in
            [Yy]* )
                if [[ "$action" == "install" ]]; then
                    { cleanup_ns && echo && \
                    $h install ${release_name} . $@ ;} || die "failed to deploy";
                else
                    $h upgrade ${release_name} . $@ || die "failed to upgrade";
                fi
                echo
                [ $watching = false ] || run_watcher
                break;;
            [Nn]* ) break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
    popd &>/dev/null
}

function run_watcher() {
    $k get pods -w
}

usage="$(basename $0) [-h] [--upgrade] [-u] [-w] [-n <ns>] [-c <cluster id> ][helm arguments] -- the tool to deploy PMS and its dependent services into given ns

where:
    -h, --help
        show this help text
    --upgrade
        Helm upgrade the integrated helm chart
    -l, --local
        if given, the local build of PMS is used
    -n, --namespace <ns>
        namespace for the deployment. The default is ${USER}-ns.
    -r, --remove
        if given, the script will run uninstall the existing release and cleanup given namespace, then exit.
    -u, --run-update
        run helm dependency update or not before deploying
    -w, --watch
        watch for changes of deploying pods. Disabled by default.
    [helm arguments] parameters and their values that you would put it after 'helm -n <ns> install release_name [helm arguments]'.

E.g.:
$ ./deploy.sh -n zrdtuan-ns

"

# Default values
use_local_build=false
run_update_dependency=false
namespace=${USER}-ns
watching=false
helm_debug=false
undeploy=false
helm_upgrade=false
while [[ "$#" -gt 0 && $1 != "--set" ]]; do
    case "$1" in
        -h|--help)
            echo "$usage"
            exit 0
            ;;
        -d|--debug)
            helm_debug=true
            ;;
        -n|--namespace)
            namespace=$2
            shift
            ;;
        -l|--local)
            use_local_build=true
            ;;
        -r|--remove)
            undeploy=true
            ;;
        -u|--run-update)
            run_update_dependency=true
            ;;
        -w|--watch)
            watching=true
            ;;
        --upgrade)
            helm_upgrade=true
            undeploy=false #reset undeploy to false to avoid mistakes from user
            ;;
    esac
    shift
done

# code will refer to the short form, $k, instead of the long form 'kubectl -n $namespace'
k="kubectl -n $namespace"
h="helm -n $namespace"
[[ $helm_debug = true ]] && h="helm -n $namespace --debug"

release_name="cert-manager"
if [ $undeploy = true ] ; then
  cleanup_ns
  echo "Finished cleanup namespace $namespace of $release_name. Exit!!! "
  exit 0
fi

# force 'update' if the charts folder does not exist even told 'ignnore update'
[[ $run_update_dependency = false && -d "charts" ]] || dependency_update

# replace official PMS helm chart with local build
[ $use_local_build = true ] && replace_with_local_build

if [ $helm_upgrade = true ] ; then
    run_helm_command upgrade $@ --set ck-application.aws.key=$AWS_ACCESS_KEY_ID --set ck-application.aws.secret=$AWS_SECRET_ACCESS_KEY
else
    run_helm_command install $@ --set ck-application.aws.key=$AWS_ACCESS_KEY_ID --set ck-application.aws.secret=$AWS_SECRET_ACCESS_KEY
fi