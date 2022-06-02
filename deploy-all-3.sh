#!/bin/bash

source ~/bin/set_environment.sh

COMPONENTS=("cspace-solr-ucb" "cspace-webapps-common" "projects/radiance")

# nb: on aws, blacklight deployment use the 'prod' environment always
SCRIPTS=("utilities/redeploy-etl.sh VERSION ${ENVIRONMENT}" "deploy-ucb.sh -a -v VERSION -e prod" "deploy-all.sh VERSION prod")

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