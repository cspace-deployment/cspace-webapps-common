#!/bin/bash
# a helper for deploying the django webapps to ALL ucb deployments on rtl 'managed servers'
#
# while it does work, it is really more of an example script...
# ymmv! use it if it really helps!
#
# usage:
#
# to deploy a particular version (i.e. tag)
# ./deploy_all.sh 5.1.0-rc3
#
# to deploy the repo "as is" (e.g. for development perhaps, where you may have uncommitted changes
# ./deploy_all.sh
#

cd ~/dazzle
for t in bampfa botgarden cinefiles pahma ucjeps
do
  # make sure the repo is clean and tidy
  git clean -fd
  git reset --hard
  # now set things up
  ~/setup.sh configure prod $1
  ~/setup.sh deploy ${t} $1
done
