#!/bin/bash

# compute some usages statistics for the image server

YEAR=`date +%Y`
MONTH=`date +%m`

grep imageserver.image /cspace/monitor/*.django.log | cut -f2- -d":" | cut -f1-3,7,8 | perl -pe 's/ seconds//;s#blobs/##;s/ +//g;s/\t\t/\t/g;' > is.extract.csv
perl -pe 's#/derivatives/(.*?)/content#\t\1#;s#/content#\tOriginal#' is.extract.csv > i2.csv
rm is.extract.csv
perl -ne 'print if /\t(Thumbnail|Medium|Original|Large|OriginalJpeg)\t/' i2.csv > imageserver.gets.csv &
perl -ne 'print unless /\t(Thumbnail|Medium|Original|Large|OriginalJpeg)\t/' i2.csv > imageserver.errors.csv &
wait
rm i2.csv
echo "<html>"
echo "<h3>Some ImageServer Usage Statistics"
echo "<h4>ImageServer gets by derivative type, since 2020</h4><pre>"
cut -f5 imageserver.gets.csv | sort | uniq -c
echo
echo "</pre><h4>ImageServer gets by museum, since 2020</h4><pre>"
cut -f1 imageserver.gets.csv | sort | uniq -c
echo
echo "</pre><h4>ImageServer gets by derivative, this month, ${YEAR}-${MONTH}</h4><pre>"
grep "${YEAR}-${MONTH}-" imageserver.gets.csv | cut -f5 | sort | uniq -c
echo
echo "</pre><h4>ImageServer gets by museum, this month, ${YEAR}-${MONTH}</h4><pre>"
grep "${YEAR}-${MONTH}-" imageserver.gets.csv | cut -f1 | sort | uniq -c
echo
echo "</pre><h4>ImageServer gets by month for the last year</h4><pre>"
cut -f2 imageserver.gets.csv | cut -c1-7 | sort -r | uniq -c | head -12
echo
echo "</pre><h4>ImageServer request errors</h4><pre>"
wc -l imageserver.errors.csv
echo "</pre></html>"
gzip -f imageserver.gets.csv
# rm imageserver.errors.csv