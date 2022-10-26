#!/bin/bash
#
# script to help deploy django webapps
#
# essentially a type of 'make' file.
#
# the project can be set up to run in Prod, Dev, and Pycharm environments with 'configure'
# the project can be customized for any of the UCB deployments with 'deploy'
# individual webapps can be enabled and disabled
#
# this bash script does the following:
#
# 1. 'deploy':
#     a. copies and configures the code for one of the 5 UCB deployments
#     b. "npm install" builds the needed js components
#     c. if running on a UCB server (i.e. ubuntu, which is detected automatically),
#        rsyncs the code to the runtime directory and makes symlinks in /var/www
# 2. other maintainance functions: 'disable' or 'enable' individual webapps
# 3. 'show' show what apps are installed

# exit on errors...
# TODO: uncomment this someday when the script really can be expected to run to completion without errors in all circumstances
# set -e

# TODO: this script sets env vars but is not part of this repo or deployment suite
# it is found in the cspace-solr-ucb repo in utilities/
# there is only one place where this is used: in finding the webapp config directories, via HOMEDIR
source ~/set_platform.sh

export COMMAND=$1
# the second parameter can stand for 2 different things!
export WEBAPP=$2
export TENANT=$2
export DEPLOYMENT=$3

# nb: version is optional. if not present, current repo, with or without changes is used...
export VERSION="$4"

export CONFIGDIR=${HOME}/cspace-webapps-ucb
export BASEDIR=${HOME}/cspace-webapps-common

# NB: we need python3, in fact python>=3.8 but the command for this varies from system to
# system. using 'python3' below works for RTL deployments on EC2 running Ubuntu 20.x
# YYMV!
export PYTHON=python3

# we don't export this value as others might be using it
YYYYMMDDHHMM=$(date +%Y%m%d%H%M)
export RUNDIR=${HOME}/${YYYYMMDDHHMM}/${TENANT}

function build_project() {
  # TODO: fix this hack to make the small amount of js work for all the webapps
  if [[ "$OSTYPE" == "linux-gnu" ]]; then
    perl -i -pe 's/..\/..\/suggest/\/$ENV{TENANT}\/suggest/' client_modules/js/PublicSearch.js
  else
    # newer npm versions than those on RTL servers need this
    export NODE_OPTIONS=--openssl-legacy-provider
  fi

  # build the javascript
  npm install
  ./node_modules/.bin/webpack
  # disable eslint for now, until we address the errors it detects
  #./node_modules/.bin/eslint client_modules/js/app.js

  # TODO: for now, generate secret here and not in settings.py
  cd cspace_django_site
  $PYTHON -c "from secret_key_gen import *; generate_secret_key('secret_key.py');"
  cd ..
  # now we can go ahead and complete the configuration
  $PYTHON manage.py makemigrations
  $PYTHON manage.py migrate --noinput
  $PYTHON manage.py loaddata fixtures/*.json
  # get rid of the existing static_root to force django to rebuild it from scratch
  rm -rf static_root/
  $PYTHON manage.py collectstatic --noinput

  # the runtime directory is ${HOME}/YYYYMMDDHHMM/M
  # (where M is the museum and YYYYMMDDHHMM is today's date)
  # if not Linux, e.g. Darwin (= development), configure everything in the current directory ...
  # rsync the "prepped and configged" files to the runtime directory
  rsync -a --delete --exclude node_modules --exclude .git --exclude .gitignore . ${RUNDIR}

  # we assume the user has all the needed config files for this museum in ${HOMEDIR}/config
  rm -rf ${RUNDIR}/config/
  ln -s ${HOMEDIR}/config/${TENANT} ${RUNDIR}/config

  # on RTL ubuntu servers, go ahead and symlink the runtime directory to
  # the location apache/passenger expects
  if [[ "$OSTYPE" == "linux-gnu" ]]; then
    echo "symlinking ${RUNDIR} as /var/www/${TENANT}"
    rm -f /var/www/${TENANT}
    ln -s ${RUNDIR} /var/www/${TENANT}
  fi

  echo "*************************************************************************************************"
  echo "The configured CSpace system is in:"
  grep 'hostname' ${RUNDIR}/config/main.cfg
  echo "*************************************************************************************************"
}

if [ $# -lt 2 -a "$1" != 'show' ]; then
  echo "Usage: $0 <enable|disable|deploy|show> <TENANT|CONFIGURATION|WEBAPP> <prod|dev|pycharm> (VERSION)"
  echo
  echo "where: TENANT = 'default' or the name of a deployable tenant"
  echo "       CONFIGURATION = <pycharm|dev|prod>"
  echo "       WEBAPP = one of the available webapps, e.g. 'search' or 'ireports'"
  echo "       VERSION = (optional) one of the available release candidates (tags)"
  echo
  echo "e.g. $0 disable ireports"
  echo "     $0 deploy botgarden prod 5.1.0-rc8"
  echo "     $0 deploy pahma pycharm"
  echo "     $0 show"
  echo
  exit 0
fi

if [[ ! -e manage.py ]]; then
  echo "No manage.py found. This script must be run from within the django project directory"
  echo
  exit 1
fi

if [[ "${COMMAND}" = "deploy" ]]; then

  if [[ ${USER} == 'app_cspace' ]]; then
    echo
    echo "USER is 'app_cspace', assuming deployment is on AWS/EC2"
    export GLOBAL=aws
    echo
  elif [[ ${USER} == 'app_webapps' ]]; then
    echo
    echo "Assuming deployment is on RTL server"
    export GLOBAL=rtl
    echo
  else
    echo
    echo "Assuming deployment is local"
    export GLOBAL=local
    echo
  fi

  if [[ ! -d "${CONFIGDIR}" ]]; then
    echo
    echo "The repo containing the configuration files (${CONFIGDIR}) does not exist"
    echo "Please either create it (e.g. by cloning it from github)"
    echo "or edit this script to set the correct path"
    echo
    exit 1
  else
    echo "updating ${CONFIGDIR} to HEAD of main branch"
    cd "${CONFIGDIR}"
    git checkout main
    git pull -v
  fi

  if [[ ! -d "${BASEDIR}" ]]; then
    echo
    echo "The repo containing the webapps (${BASEDIR}) does not exist"
    echo "Please either create it (e.g. by cloning it from github)"
    echo "or edit this script to set the correct path"
    echo
    exit 1
  else
    cd "${BASEDIR}"
  fi

  if [[ ! -f "cspace_django_site/extra_${DEPLOYMENT}.py" ]]; then
    echo
    echo "Can't configure '${DEPLOYMENT}': use 'pycharm', 'dev', or 'prod'"
    echo
    exit 1
  fi

  if [[ ! -d "${CONFIGDIR}/${TENANT}" ]]; then
    echo
    echo "Can't deploy tenant ${TENANT}: ${CONFIGDIR}/${TENANT} does not exist"
    echo
    exit 1
  fi

  # check for indicated version (tag), if provided...
  if [[ $VERSION != "main" ]]; then
    TAGS=$(git tag --list ${VERSION})
    if [[ ${TAGS} ]]; then
      echo "will build version $VERSION"
    else
      echo "could not find version $VERSION"
      exit 1
    fi
  else
    echo
    echo "'main' specified; deploying code as is, not from clean repo."
  fi

  if [[ -e ${RUNDIR} ]]; then
    echo
    echo "Cowardly refusal to overwrite existing runtime directory ${RUNDIR}"
    echo "Remove or rename ${RUNDIR}, then try again."
    exit 1
  fi
  echo "Making and populating runtime directory ${RUNDIR}"
  mkdir -p ${RUNDIR}

  # ok, everything checks out... let's get going..

  # do all configuration in ${HOME}/working_dir, which is then rync'd to the runtime directory
  # if version is specified, make a 'clean' clone and checkout the tag
  # otherwise make copy of this exact repo and do the configuration work there
  rm -rf ${HOME}/working_dir
  if [[ $VERSION != "main" ]]; then
    THIS_REPO=`git config --get remote.origin.url`
    git clone ${THIS_REPO} ${HOME}/working_dir
    cd ${HOME}/working_dir/
    git -c advice.detachedHead=false checkout ${VERSION}
  else
    rsync -a . ${HOME}/working_dir
    cd ${HOME}/working_dir
  fi

  cp cspace_django_site/extra_${DEPLOYMENT}.py cspace_django_site/extra_settings.py
  cp cspace_django_site/webapps_global_config_${GLOBAL}.py cspace_django_site/webapps_global_config.py

  rm -f config/*
  rm -f fixtures/*

  # use 'default' configuration for this tenant from github, only initially, for configuration
  cp ${CONFIGDIR}/${TENANT}/config/* config
  cp ${CONFIGDIR}/${TENANT}/fixtures/* fixtures
  # note that in some cases, this cp will overwrite customized files in the underlying contributed apps
  # in cspace-webapps-common. that is the intended behavior!
  cp -r ${CONFIGDIR}/${TENANT}/apps/* .
  cp ${CONFIGDIR}/${TENANT}/project_urls.py cspace_django_site/urls.py
  cp ${CONFIGDIR}/${TENANT}/project_apps.py cspace_django_site/installed_apps.py
  cp client_modules/static_assets/cspace_django_site/images/header-logo-${TENANT}.png client_modules/static_assets/cspace_django_site/images/header-logo.png
  # just to be sure, we start over with the database...
  rm -f db.sqlite3

  # update the version file
  $PYTHON common/setversion.py

  # build js library, populate static dirs, rsync code to runtime dir if needed, etc.
  build_project
  echo
  echo "*************************************************************************************************"
  echo "Don't forget to check config/${TENANT}/main.cfg if necessary and the rest of the"
  echo "configuration files in config/ (these are .cfg, .json, and .csv files mostly)"
  echo "*************************************************************************************************"
  echo
elif [[ "${COMMAND}" = "disable" ]]; then
  perl -i -pe "s/('${WEBAPP}')/# \1/" cspace_django_site/installed_apps.py
  perl -i -pe "s/(path)/# \1/ if /${WEBAPP}/" cspace_django_site/urls.py
  echo "Disabled ${WEBAPP}"
elif [[ "${COMMAND}" = "enable" ]]; then
  perl -i -pe "s/# *('${WEBAPP}')/\1/" cspace_django_site/installed_apps.py
  perl -i -pe "s/# *(path)/\1/ if /${WEBAPP}/" cspace_django_site/urls.py
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
  echo "Enabled ${WEBAPP}"
elif [[ "${COMMAND}" = "show" ]]; then
  echo
  echo "Installed apps:"
  echo
  echo -e "from cspace_django_site.installed_apps import INSTALLED_APPS\nfor i in INSTALLED_APPS: print(i)" | $PYTHON
  echo
else
  echo "${COMMAND} is not a recognized command."
fi
