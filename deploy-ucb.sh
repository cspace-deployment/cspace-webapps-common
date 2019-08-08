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
      echo "to deploy the clean master branch for all ucb tenants (e.g. for development perhaps, where you may have uncommitted changes)"
      echo "./deploy_ucb.sh -a"
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

cd ~/cspace-webapps-common/
for t in $MUSEUMS
do
  # make sure the repo is clean and tidy
  git clean -fd
  git reset --hard
  # now set things up
  ./setup.sh configure prod $1
  ./setup.sh deploy ${t} $1
done