#!/usr/bin/env bash

if [[ $# -ne 3 ]] ; then
  echo "three arguments required: filepath museum direction (from/to)"
  exit 1
fi

BL_ENVIRONMENT=`/usr/bin/curl -s -m 5 http://169.254.169.254/latest/meta-data/tags/instance/BL_ENVIRONMENT`
if [[ -z $BL_ENVIRONMENT || ( "$BL_ENVIRONMENT" != "dev" && "$BL_ENVIRONMENT" != "qa" && "$BL_ENVIRONMENT" != "prod" ) ]]; then
	echo "Could not fetch BL_ENVIRONMENT, are you sure you're on AWS?"
	exit 1
fi
BL_ENVIRONMENT="blacklight-${BL_ENVIRONMENT}"

s=0
if [[ "$3" == "to" ]] ; then
  for i in {1..2}; do
    echo "/usr/bin/aws s3 cp '/tmp/$1' s3://${BL_ENVIRONMENT}/bmu/$2/$1"
    /usr/bin/aws s3 cp --quiet "/tmp/$1" s3://${BL_ENVIRONMENT}/bmu/$2/$1 && s=0 && break || s=$?
    echo "failed with exit code $s. retrying. attempt $i"
    sleep 1
  done
  rm -f "/tmp/$1"
  exit $s
elif [[ "$3" == "from" ]] ; then
  for i in {1..2}; do
    echo "/usr/bin/aws s3 cp 's3://${BL_ENVIRONMENT}/bmu/$2/$1' /tmp"
    /usr/bin/aws s3 cp --quiet "s3://${BL_ENVIRONMENT}/bmu/$2/$1" /tmp
    s=$?
    [ -e "/tmp/$1" ] && exit 0
    echo "failed with exit code $s. retrying. attempt $i"
    sleep 1
  done
  # did not work
  echo "copy 'from' failed. giving up."
  exit 1
else
  echo "direction must be either from or to"
  exit 1
fi
