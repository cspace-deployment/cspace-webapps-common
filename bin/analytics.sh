#!/bin/bash

# generate some useful stats on database content and webapp and portal use

source ${HOME}/pipeline-config.sh

YEAR=`date +%Y`
MONTH=`date +%m`

cd /cspace/monitor
./checklogs.sh | mail -r "cspace-support@lists.berkeley.edu" -s "Access Log Analysis" ${TECH_LEAD}
# analyze and summarize the django logs and solr cores, keep a copy of an extract of the other vhost logs
./analyze.sh >> analytics.log  2>&1 ; ./corestats.sh >> analytics.log 2>&1
# count media uploaded via bmu
wc -l /cspace/bmu/*/*.processed.csv | perl -pe 's/^ *(\d+) /\1\t/;s#/cspace/bmu/(.*)#\1#;s#/#\t#g;s/.processed.csv//' > /cspace/monitor/bmu-counts.csv
# count ip addresses in logs
cat /var/log/apache2/*/*/*.log | cut -f1 -d" " | sort | uniq -c | sort -rn | head -50 > /cspace/monitor/${YEAR}-${MONTH}-ips.txt
# compute some imageserver stats
./extract-imageserver-gets.sh > /var/www/static/imageserver-stats.html
# recompute goaccess stats daily
${HOME}/bin/goaccess.sh
# make a list of all the metrics for easy reference
${HOME}/bin/make-metrics.sh
