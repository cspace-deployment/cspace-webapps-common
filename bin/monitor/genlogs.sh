#!/bin/bash
export t=$1
cat /cspace/webapps_logs/${t}.webapps.* | perl -ne 'print if /\d{4}\-\d{2}-\d{2}/' |\
 grep INFO | grep common.utils | grep -v Generating | grep -v  startup | grep -v csvdump | grep -v KeyError |\
 grep -v "Solr search failed" | grep -v 'start imaginator' | grep -v 'Derivatives served' | grep -v "bmu online" |\
 grep -v SMBConnection | grep -v watermark | grep -v urllib3 | grep -v AuthN | grep -v override | grep -v 'as working directory for images' |\
 grep -v "no searchValues set" | grep -v 'start search' | grep -v 'start imagebrowser' | grep -v "Solr search succeeded" | grep -v "Configuration for " |\
 grep -v accountperms | grep -v delete |\
 perl -pe 's/ :: /\t/g' \
 > ${t}.temp1

 perl -pe 's#^(.*?) (.*?) (\w+) common.utils (.*?)\t#$ENV{t}\t\1\t\2\t\3\t\4.#' ${t}.temp1 > ${t}.temp2

 #perl -pe 's#^(.*?) (.*?) (\w+) common.utils (.*?) :: (.*?) :: (.*?)(end| )::? (.*?) (:: )?(.*?) ?#$ENV{t}\t\1\t\2\t\3\t\4\t\5\t\6\t\7\t\8#'\
cat ${t}.temp2 ${t}.django.log | perl -ne 'print unless /text:.*?(rotogravure|Monterey|prominent|preserve|glazed|ZAP)/' | sort -u > ${t}.temp3
mv ${t}.temp3 ${t}.django.log
rm ${t}.temp*
# for counting, eliminate initial query records, only count results.list records
grep -v 'query:' ${t}.django.log | grep -v "toolbox.end" |\
  perl -pe 's/bmu.id/bmu.id\t/' | cut -f5 | perl -pe 's/:\d+//;' | sort |uniq -c | sort -rn | head -40 > ${t}.logsummary.txt &
echo "	${t}" > ${t}.temp.txt
echo -e "aafirst log date\t`cut -f2 ${t}.django.log | sort -u | perl -pe 's/\// /g' | sort -k3 -k2M -k1 | head -1`" >> ${t}.temp.txt
echo -e "aalast log date\t`cut -f2 ${t}.django.log | sort -u | perl -pe 's/\// /g' | sort -k3 -k2M -k1 | tail -1`" >> ${t}.temp.txt
echo -e "aandays of activity\t`cut -f2 ${t}.django.log | sort -u | perl -pe 's/\// /g' | sort -k3 -k2M -k1 | wc -l`" >> ${t}.temp.txt
wait
perl -ne 's/^ *(\d+) (.*)$/\2\t\1/;print unless (length > 35)' ${t}.logsummary.txt | sort >> ${t}.temp.txt
