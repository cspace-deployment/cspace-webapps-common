grep imageserver.image /cspace/monitor/*.django.log | cut -f2- -d":" | cut -f1-3,7,8 | perl -pe 's/ seconds//;s#blobs/##;s/ +//g;s/\t\t/\t/g;' > is.extract.csv
perl -pe 's#/derivatives/(.*?)/content#\t\1#;s#/content#\tOriginal#' is.extract.csv > i2.csv
rm is.extract.csv
perl -ne 'print if /\t(Thumbnail|Medium|Original|Large|OriginalJpeg)\t/' i2.csv > imageserver.gets.csv &
perl -ne 'print unless /\t(Thumbnail|Medium|Original|Large|OriginalJpeg)\t/' i2.csv > imageserver.errors.csv &
wait
cut -f5 imageserver.gets.csv | sort | uniq -c &
wc -l imageserver.errors.csv
wait
rm i2.csv

