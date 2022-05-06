#!/bin/bash

if ! grep -q " $1 " <<< " prod dev "; then
    echo "please specify and argument, either dev or prod"
fi

ENVIRONMENT=$1

COMPONENTS=("cspace-solr-ucb" "cspace-webapps-common" "projects/radiance")
SCRIPTS=("utilities/redeploy-etl.sh VERSION ${ENVIRONMENT}" "deploy-ucb.sh -a -v VERSION -e ${ENVIRONMENT}" "deploy-all.sh VERSION ${ENVIRONMENT}")

for (( i=0; i<${#COMPONENTS[@]}; i++ )); do
    REPO=${COMPONENTS[$i]}
    SCRIPT=${SCRIPTS[$i]}
    cd ${HOME}/${REPO}
    git checkout main
    git pull -v
    git clean -fd
    TAG=`git tag | tail -1`
    SCRIPT=${SCRIPT/VERSION/$TAG}
    SCRIPT="${HOME}/${REPO}/${SCRIPT}"
    DATE=`date +%Y%m%d%H%M`
    echo "${SCRIPT}"
    cd
    eval "${SCRIPT} > release-${REPO/\//-}-${DATE}.txt 2>&1 &"
done

wait

