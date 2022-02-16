#!/bin/bash
# a helper for deploying the django webapps to ucb ENVIRONMENTs on rtl 'managed servers'
#
# while it does work, it is really more of an example script...
# ymmv! use it if it really helps!
#

VERSION=""  # Default to no version
ENVIRONMENT="prod" # Default to production environment
WHOLE_LIST="bampfa botgarden cinefiles pahma ucjeps"

while [[ $# -gt 0 ]] ;
do
  opt="$1";
  shift;
  case ${opt} in
    '-h' )
      echo "usage:"
      echo
      echo "./deploy_ucb.sh [-v VERSION] [-e {dev,prod,pycharm}] MUSEUM (or -a for all museums)"
      echo
      echo "to deploy a particular version for all ucb museums(i.e. tag)"
      echo "./deploy_ucb.sh -a -v 5.1.0-rc3 -e prod"
      echo
      echo "to deploy a particular version (i.e. tag) for pahma and cinefiles"
      echo "./deploy_ucb.sh pahma -v 5.1.0-rc3 cinefiles -e dev"
      echo
      echo "nb: assumes you have the two needed repos set up in the standard RTL way. See the README.md for details."
      echo "    if no version is specified, this repo is copied and used as the source ... i.e. including"
      echo "    uncommitted changes. Good for testing!"
      echo "    if no environment is specified, production is assumed"
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
    '-e' )
      ENVIRONMENT=$1 ; shift
    ;;
    * )
    if [[ ! $MUSEUMS =~ .*$opt.* ]]
    then
        MUSEUMS="${MUSEUMS} $opt"
    fi
    ;;
  esac
done

echo "museums:     ${MUSEUMS}"
echo "environment: ${ENVIRONMENT}"
echo "version:     ${VERSION}"

cd ~/cspace-webapps-common/

for t in $MUSEUMS
do
  ./setup.sh deploy ${t} ${ENVIRONMENT} ${VERSION}
done
