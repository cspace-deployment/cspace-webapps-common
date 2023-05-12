#!/bin/bash
LOGS=/var/log/apache2/webapps*/*/*access.log
source ${HOME}/pipeline-config.sh

echo "Q&D access log analysis"
echo
echo "500s:"
echo
grep " 500 " $LOGS | grep -v -i bot | grep -v imageserver | perl -pe 's/^.*?\[//;s/ .*?\"/ "/;s/ "\-" .*//' |\
 sort -t ' ' -k 1.8,1.11rn -k 1.3,1.5rM -k 1.1,1.2rn -k 1.13,1.14rn -k 1.15,1.16rn -k 1.17,1.19rn | head -20
echo

echo "403:"
echo
grep " 403 " $LOGS | grep -v -i bot | grep -v imageserver | perl -pe 's/^.*?\[//;s/ .*?\"/ "/;s/ "\-" .*//' |\
 sort -t ' ' -k 1.8,1.11rn -k 1.3,1.5rM -k 1.1,1.2rn -k 1.13,1.14rn -k 1.15,1.16rn -k 1.17,1.19rn | head -20
echo

echo "Dates:"
echo
cut -f3 -d"-" $LOGS | cut -f1 -d ":" | perl -pe 's/ \[//' | sort -t ' ' -k 1.8,1.11n -k 1.4,1.6M -k 1.1,1.2n |\
 uniq -c | tac | perl -pe 's/^ *(\d+) /\1\t/' > ${HOMEDIR}/webapps_logs/webapps.log.counts.csv
head -100 ${HOMEDIR}/webapps_logs/webapps.log.counts.csv
echo
echo "HTTP Codes:"
echo
cat $LOGS | grep -v webapps | perl -pe 's/^.*? (\d\d\d) .*/\1/' | sort | uniq -c | sort -rn | head -100
echo
echo "HTTP Requests:"
echo
grep HTTP $LOGS | cut -f6 -d" " | sort | uniq -c | sort -rn | perl -pe 's/"//g' | head -100
echo