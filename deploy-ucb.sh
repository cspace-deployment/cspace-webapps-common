#!/bin/bash
# a helper for deploying the django webapps to ucb deployments on rtl 'managed servers'
#
# while it does work, it is really more of an example script...
# ymmv! use it if it really helps!
#

VERSION=""  # Default to no version
WHOLE_LIST="bampfa botgarden cinefiles pahma ucjeps"

while [[ $# -gt 0 ]] ;
do
  opt="$1";
  shift;
  case ${opt} in
    '-h' )
      echo "usage:"
      echo
      echo "to deploy a particular version for all ucb museums(i.e. tag)"
      echo "./deploy_ucb.sh -a -v 5.1.0-rc3"
      echo
      echo "to deploy a particular version (i.e. tag) for pahma and cinefiles"
      echo "./deploy_ucb.sh pahma -v 5.1.0-rc3 cinefiles"
      echo
      echo "nb: assumes you have the two needed repos set up in the standard RTL way. See the README.md for details."
      echo
      exit 0
    ;;
    '-a' )
      MUSEUMS=$WHOLE_LIST
      echo $MUSEUMS
    ;;
    '-v' )
      VERSION=$1 ; shift;
    ;;
    * )
    if [[ ! $MUSEUMS =~ .*$opt.* ]]
    then
        MUSEUMS="${MUSEUMS} $opt"
    fi
    ;;
  esac
done

# make sure the ucb custom repo is clean and tidy
cd ~/cspace-webapps-ucb/
git clean -fd
git reset --hard
git checkout master
git pull -v
cd ~/cspace-webapps-common/

# backup the existing config files
./backup-config.sh

for t in $MUSEUMS
do
  echo "Cleaning up to deploy ${t}..."
  # make sure the repo is clean and tidy for each tenant
  git clean -fd
  git reset --hard
  git checkout master
  git pull -v
  # now set things up
  ./setup.sh configure prod $VERSION
  ./setup.sh deploy ${t} $VERSION
done
