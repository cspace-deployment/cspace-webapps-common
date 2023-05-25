#!/bin/bash
# bring all clones of repos up to date and delete all old release candidates ('rc-*')

read -r -p "Really remove all *-rc release candidate tags? [y/N] " response
if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    echo
    echo "Quitting, leaving tags alone!"
    exit 1
fi

cd
for COMPONENTS in cspace-solr-ucb cspace-webapps-ucb cspace-webapps-common projects/radiance; do
  cd ~/${COMPONENTS}
  git checkout main
  git pull -v
  git tag | grep rc | xargs git push --delete origin
  git tag | grep rc | xargs git tag -d
  git tag
done
