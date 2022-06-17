#!/bin/bash

# generate some useful stats on database content and webapp and portal use

source ${HOME}/pipeline-config.sh

/cspace/monitor/checklogs.sh | mail -r "cspace-support@lists.berkeley.edu" -s "Access Log Analysis" jblowe@berkeley.edu
# analyze and summarize the django logs and solr cores, keep a copy of an extract of the other vhost logs
cd /cspace/monitor ; ./analyze.sh >> analytics.log  2>&1 ; ./corestats.sh >> analytics.log 2>&1
wc -l /cspace/bmu/*/*.processed.csv | perl -pe 's/^ *(\d+) /\1\t/;s#/cspace/bmu/(.*)#\1#;s#/#\t#g;s/.processed.csv//' > /cspace/monitor/bmu-counts.csv
# recompute goaccess stats daily
${HOME}/bin/goaccess.sh
${HOME}/bin/make-metrics.sh
