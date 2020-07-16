#!/bin/bash
#
# script to help deploy webapps
#
# essentially a type of 'make' file.
#
# the project can be set up to run in Prod, Dev, and Pycharm environments with 'configure'
# the project can be customized for any of the UCB deployments with 'deploy'
# individual webapps can be enabled and disabled
#
# this bash script does the following:
#
# 1. 'configure' copies the appropriate "extra settings" file for the environment
# 2. 'deploy':
#     a. copies and configures the code for one of the 5 UCB deployments
#     b. "npm builds" the needed js components
#     c. if running on a UCB server (which is detected automatically), rsyncs the code to the runtime directory
# 3. other maintainance functions: 'disable' or 'enable' individual webapps
#

# exit on errors...
# TODO: uncomment this someday when the script really can be expected to run to completion without errors
# set -e

COMMAND=$1
# the second parameter can stand for several different things!
WEBAPP=$2
TENANT=$2
DEPLOYMENT=$2

# nb: version is optional. if not present, current repo, with or without changes is used...
VERSION="$3"

CONFIGDIR=~/cspace-webapps-ucb

PYTHON=python3

function buildjs()
{
    # TODO: fix this hack to make the small amount of js work for all the webapps
    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        export TENANT="$TENANT"
        perl -i -pe 's/..\/..\/suggest/\/$ENV{TENANT}\/suggest/' client_modules/js/PublicSearch.js
    fi

    npm install
    npm build
    ./node_modules/.bin/webpack
    # disable eslint for now, until we address the errors it detects
    #./node_modules/.bin/eslint client_modules/js/app.js
}

function deploy()
{
    buildjs $1
    # if this is running on an RTL server, the runtime directory is ~/M/YYYYMMDD
    # (where M is the museum and YYYYMMDD is today's date)
    # if not Linux, e.g. Darwin (= development), configure everything in the current directory ...
    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        YYYYMMDD=`date +%Y%m%d`
        RUNDIR=~/${YYYYMMDD}/$1
        if [[ -e ${RUNDIR} ]]; then
            echo "Cowardly refusal to overwrite existing runtime directory ${RUNDIR}"
            echo "Remove or rename ${RUNDIR}, then try again."
            exit 1
        fi
        echo "Making and populating runtime directory ${RUNDIR}"
        mkdir -p ${RUNDIR}
        # copy the built files to the runtime directory, but leave the config files as they are
        rsync -av --delete --exclude node_modules --exclude .git --exclude .gitignore --exclude config . ${RUNDIR}

        # copy the most recent backup of the config files into this new runtime directory
        # nb: presumes that these are the right ones! any changes to configuration needed
        # for this release will need to be applied (by hand, presumably) in advance
        # of relinking.
        # TODO: need to ineluctably save the current config so that the following will work.
        cp -r ~/backup/$1/config ${RUNDIR}

        cd ${RUNDIR}
    fi

    echo "*************************************************************************************************"
    echo "The configured CSpace system is:"
    grep 'hostname' ${RUNDIR}/config/main.cfg
    echo "*************************************************************************************************"

    # now we can go ahead and complete the configuration
    $PYTHON manage.py migrate --noinput
    $PYTHON manage.py loaddata fixtures/*.json
    # get rid of the existing static_root to force django to rebuild it from scratch
    rm -rf static_root/
    $PYTHON manage.py collectstatic --noinput
}

function check_version()
{

    if [[ $VERSION != "" ]]; then
        if [[ $(git status -s) ]]; then
            echo
            echo 'FYI, uncommitted changes or untracked files were found and version $VERSION was specified.'
            echo
            echo 'Initial deployments of a particular version must be from a "clean" branch.'
            echo
            echo 'Cowardly refusal to proceed; please clean up and try again...'
            echo
            echo 'e.g. something like the following'
            echo
            echo 'git clean -fd'
            echo 'git reset --hard'
            echo 'git pull -v'
            echo
            exit 1
            # read -p "continue as is? (y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
        fi
        git checkout ${VERSION}

    else
        echo
        echo "No version specified; deploying code as is, but with specified customizations."
    fi
}

if [ $# -lt 2 -a "$1" != 'show' ]; then
    echo "Usage: $0 <enable|disable|deploy|configure|show> <TENANT|CONFIGURATION|WEBAPP> (VERSION)"
    echo
    echo "where: TENANT = 'default' or the name of a deployable tenant"
    echo "       CONFIGURATION = <pycharm|dev|prod>"
    echo "       WEBAPP = one of the available webapps, e.g. 'search' or 'ireports'"
    echo "       VERSION = (optional) one of the available release candidates (tags)"
    echo
    echo "e.g. $0 disable ireports"
    echo "     $0 configure pycharm"
    echo "     $0 deploy botgarden 5.1.0-rc8"
    echo "     $0 show"
    echo
    exit 0
fi

if [[ ! -e manage.py ]]; then
    echo "No manage.py found. This script must be run in the django project directory"
    echo
    exit 1
fi

if [[ "${COMMAND}" = "disable" ]]; then
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
elif [[ "${COMMAND}" = "configure" ]]; then
    if [[ ! -f "cspace_django_site/extra_${DEPLOYMENT}.py" ]]; then
        echo "Can't configure '${DEPLOYMENT}': use 'pycharm', 'dev', or 'prod'"
        echo
        exit
    fi

    # checkout indicated version, if any...
    check_version

    cp cspace_django_site/extra_${DEPLOYMENT}.py cspace_django_site/extra_settings.py
    echo
    echo "*************************************************************************************************"
    echo "OK, \"${DEPLOYMENT}\" is configured. Now run ./setup.sh deploy <tenant> to set up a particular tenant,"
    echo "where <tenant> is either "default" (for non-specific tenant, i.e. nightly.collectionspace.org) or"
    echo "an existing tenant in the ${CONFIGDIR} repo"
    echo "*************************************************************************************************"
    echo
elif [[ "${COMMAND}" = "deploy" ]]; then
    if [[ ! -d "${CONFIGDIR}" ]]; then
        echo "The repo containing the configuration files (${CONFIGDIR}) does not exist"
        echo "Please either create it (e.g. by cloning it from github)"
        echo "or edit this script to set the correct path"
        echo
        exit 1
    fi

    # checkout indicated version, if any...
    check_version

    if [[ ! -d "${CONFIGDIR}/${TENANT}" ]]; then
        echo "Can't deploy tenant ${TENANT}: ${CONFIGDIR}/${TENANT} does not exist"
        echo 1
        exit
    fi

    # for now, until versions in both cspace-webapps-ucb and cspace-webapps-common are sync'd
    # we don't check the version for the 'custom webapps' repo (cspace-webapps-ucb) ...
    # cd ${CONFIGDIR}
    # check_version

    rm -f config/*
    rm -f fixtures/*

    # use 'default' configuration for this tenant from github, only initially for configuration
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
    deploy ${TENANT}
    echo
    echo "*************************************************************************************************"
    echo "Don't forget to check cspace_django_site/main.cfg if necessary and the rest of the"
    echo "configuration files in config/ (these are .cfg, .json, and .csv files mostly)"
    echo "*************************************************************************************************"
    echo
else
    echo "${COMMAND} is not a recognized command."
fi
