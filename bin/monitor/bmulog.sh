#!/bin/bash
TENANT=$1
cat /cspace/bmu/${TENANT}/*.trace.log > /tmp/${TENANT}.tmp1
perl -ne 'print unless /</' /tmp/${TENANT}.tmp1 | grep -v urllib3 | grep -v Insecure | grep -v "Error" > /tmp/${TENANT}.tmp2
perl -ne 'print if /(MEDIA:|input file:)/' /tmp/${TENANT}.tmp2 | perl -ne 'print if /(input|objectnumber)/' | grep -v failed > /tmp/${TENANT}.tmp3
perl -i -pe 's/MEDIA: objectnumber //;s#MEDIA: input  file \(fully qualified path\): /tmp/image_upload_cache_.*\b/##;s/, .*?csid: /\t/g;s/, +/\t/' /tmp/${TENANT}.tmp3
perl -ne 'if (/^.*input file: *(.*)\.inprogress\./){$f = $1;$f=~s/.tmp\/.*?\///;$f=~s/^(.{0,10})/\1\t\1/;}else{print "$f\t$_"}' /tmp/${TENANT}.tmp3 | grep -v uploading | grep -v inprogress > ${TENANT}.bmu.log
rm /tmp/${TENANT}.tmp?
