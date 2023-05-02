#!/bin/bash

source ~/bin/set_environment.sh

COMPONENTS=("cspace-solr-ucb" "cspace-webapps-common" "projects/radiance")
# nb: on aws, blacklight deployment use the 'prod' environment always
SCRIPTS=("utilities/redeploy-etl.sh VERSION ${ENVIRONMENT}" "deploy-ucb.sh -a -v VERSION -e prod" "deploy-all.sh VERSION prod")

function usage() {
  echo
  echo "usage:"
  echo
  echo "$0 release | recent | main"
  echo "   release = last 'real' release, e.g. 2.6.0, as opposed to a release candidate, e.g. 2.6.0-rc3"
  echo "   recent  = most recent tag (might be a release or a release candidate)"
  echo "   main    = tip of the main branch, as is, no update from github. who knows."
  echo
  exit 0
}

function show_parms() {
    echo "REPO:    ${REPO}"
    echo "VERSION: ${TAG}"
    if [[ "${LATEST_TAG}" != "${TAG}" ]] ; then
       echo
       echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
       echo "latest release tag is ${TAG}, but other (more recent) release candidates exist: ${LATEST_TAG}"
       echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
       echo
    fi
    echo "COMMAND: ${SCRIPT} > release-${REPO/\//-}-${DATE}.txt 2>&1 &"
    echo "========================================================================================"
    echo
}

function set_parms() {
    REPO=${COMPONENTS[$i]}
    SCRIPT=${SCRIPTS[$i]}
    cd ${HOME}/${REPO}
    git checkout main --quiet
    git pull -v --quiet
    git clean -fd --quiet
    LATEST_RELEASE=`git tag | grep -v "\-rc" | tail -1`
    LATEST_TAG=`git tag | tail -1`
    if [[ "${TARGET}" == 'main' ]]; then
        TAG='main'
    elif [[ "${TARGET}" == 'release' ]]; then
        TAG=${LATEST_RELEASE}
    elif [[ "${TARGET}" == 'recent' ]]; then
        TAG=${LATEST_TAG}
    else
        echo "parameter ${TARGET} not recognized"
        exit 1
    fi
    SCRIPT=${SCRIPT/VERSION/$TAG}
    SCRIPT="${HOME}/${REPO}/${SCRIPT}"
    DATE=`date +%Y%m%d%H%M`
}

# check the command line parameters
if [ $# -eq 1 ]; then
    TARGET="$1"
else
    usage
fi

if ! grep -q " ${TARGET} " <<< " release recent main "; then
    usage
fi

if [[ "${ENVIRONMENT}" == 'prod' && "${TARGET}" != 'release' ]]; then
    echo "On Production, this script will only deploy releases, not release candidates or 'main'"
    echo "Please try again"
    exit 1
fi

echo "========================================================================================"
echo "Deploy all 3 blacklight stack components: Solr, Django webapps, Blacklight Portals"
echo "========================================================================================"
# do this loop twice: once to update and check components, once to actually deploy
for (( i=0; i<${#COMPONENTS[@]}; i++ )); do
    set_parms
    show_parms
done

read -r -p "Continue with deploy? [y/N] " response
if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo
    echo "Quitting, leaving deployed code alone!"
    exit 1
fi

echo
echo "========================================================================================"
echo 'DEPLOY DEPLOY DEPLOY!'
echo "========================================================================================"
echo

DATE=`date +%Y%m%d%H%M`

for (( i=0; i<${#COMPONENTS[@]}; i++ )); do
    set_parms
    cd
    eval "${SCRIPT} > release-${REPO/\//-}-${DATE}.txt 2>&1 &"
done

echo
echo "Waiting for deploys to complete. Should only be a few minutes at most, please be patient"
wait

echo
echo "Checking for errors..."
echo
grep -i error release-*-${DATE}.txt | grep -v _add_error_
