#!/bin/bash

IMDSv2TOKEN=`/usr/bin/curl -s -m 5 -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60"`
ENVIRONMENT=`/usr/bin/curl -s -m 5 -H "X-aws-ec2-metadata-token: ${IMDSv2TOKEN}" http://169.254.169.254/latest/meta-data/tags/instance/BL_ENVIRONMENT`

if [[ -z $ENVIRONMENT || ( "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "qa" && "$ENVIRONMENT" != "prod" ) ]]; then
        echo "CLEANUP - $(/bin/date) - Cannot get environment, are you sure you're on AWS? Aborting!" 1>&2
        exit 1
fi

export ENVIRONMENT="${ENVIRONMENT}"
export BL_ENVIRONMENT="blacklight-${ENVIRONMENT}"

if [[ "$1" == "-v" ]]; then
  echo
  echo "ENVIRONMENT=${ENVIRONMENT}"
  echo "BL_ENVIRONMENT=${BL_ENVIRONMENT}"
  echo
fi
