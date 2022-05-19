#!/usr/bin/env bash

if [[ $# -ne 3 ]] ; then
  echo "filepath museum direction (from/to)"
  exit 1
fi

BL_ENVIRONMENT=`/usr/bin/curl -s -m 5 http://169.254.169.254/latest/meta-data/tags/instance/BL_ENVIRONMENT`
BL_ENVIRONMENT="blacklight-${BL_ENVIRONMENT}"

if [[ "$3" == "to" ]] ; then
  /usr/bin/aws s3 cp /tmp/$1 s3://${BL_ENVIRONMENT}/bmu/$2/$1
  echo "/usr/bin/aws s3 cp /tmp/$1 s3://${BL_ENVIRONMENT}/bmu/$2/$1"
  rm /tmp/$1
elif [[ "$3" == "from" ]] ; then
  /usr/bin/aws s3 cp s3://${BL_ENVIRONMENT}/bmu/$2/$1 /tmp
  echo "/usr/bin/aws s3 cp s3://${BL_ENVIRONMENT}/bmu/$2/$1 /tmp"
else
  echo "direction must be either from or to"
  exit 1
fi

