#!/usr/bin/env bash

# os-specific command to format output of 'time'
export TIME_COMMAND="/usr/bin/time -f TIME,%E,%U,%S,%C"

if [[ $# -ne 3 ]] ; then
  echo "three arguments required: filepath museum direction (from/to)"
  exit 1
fi

# sets BL_ENVIRONMENT
source ~/bin/set_environment.sh

s=0
if [[ "$3" == "to" ]] ; then
  for i in {1..1}; do
    echo "/usr/bin/aws s3 cp '/tmp/$1' 's3://${BL_ENVIRONMENT}/bmu/$2/$1'"
    ${TIME_COMMAND} /usr/bin/aws s3 cp --quiet "/tmp/$1" "s3://${BL_ENVIRONMENT}/bmu/$2/$1" && s=0 && break || s=$?
    echo "failed with exit code $s. retrying. attempt $i"
    sleep 1
  done
  rm -f "/tmp/$1"
  exit $s
elif [[ "$3" == "from" ]] ; then
  for i in {1..1}; do
    echo "/usr/bin/aws s3 cp 's3://${BL_ENVIRONMENT}/bmu/$2/$1' /tmp"
    ${TIME_COMMAND} /usr/bin/aws s3 cp --quiet "s3://${BL_ENVIRONMENT}/bmu/$2/$1" /tmp
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
