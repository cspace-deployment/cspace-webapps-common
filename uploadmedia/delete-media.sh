#!/bin/bash

perl -pe 's/ *= */=/g;s/^(\w+)/export \1/;s/^\[/#[/' /var/www/ucjeps/config/uploadmedia_batch.cfg > /tmp/bmu.cfg
source /tmp/bmu.cfg
rm /tmp/bmu.cfg
for CSID in `cat $1`
do
  #echo curl -s -S --stderr - -X DELETE https://${hostname}/cspace-services/media/$CSID --basic -u "<redacted>"
  echo curl -s -S --stderr - -X DELETE https://${hostname}/cspace-services/media/$CSID --basic -u "${username}:${password}"
  curl -s -S --stderr - -X DELETE https://${hostname}/cspace-services/media/$CSID --basic -u "${username}:${password}"
  echo
done
