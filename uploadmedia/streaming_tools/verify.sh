grep "\.aac" image_upload_cache_pahma/2019*.processed.csv > processed.aac.csv
grep "\.wav" image_upload_cache_pahma/2018*.processed.csv > processed.wav.csv
grep "\.wav" image_upload_cache_pahma/2019*.processed.csv >> processed.wav.csv
grep "\.mp4" image_upload_cache_pahma/*.processed.csv > processed.mp4.csv
perl -i -pe 's/\|/\t/g;s/\r//g;' processed.*.csv
perl -i -pe 's#image_upload_cache_pahma/##;s/.processed.csv:/\t/' processed.*.csv

grep "\.aac" image_upload_cache_pahma/2019*.original.csv > original.aac.csv
grep "\.wav" image_upload_cache_pahma/2018*.original.csv > original.wav.csv
grep "\.wav" image_upload_cache_pahma/2019*.original.csv >> original.wav.csv
grep "\.mp4" image_upload_cache_pahma/*.original.csv > original.mp4.csv
perl -i -pe 's/\|/\t/g;s/\r//g;' original.*.csv
perl -i -pe 's#image_upload_cache_pahma/##;s/.original.csv:/\t/' original.*.csv

for f in `ls original.*.csv`; do cut -f1-4 $f | LOCALE=C LANG=en_EN sort -b -t$'\t' -k2 -k1 -k4 -k3 > x ; mv x $f ; done
for f in `ls processed.*.csv`; do cut -f1-4,13-15 $f | LOCALE=C LANG=en_EN sort -b -t$'\t' -k2 -k1 -k4 -k3 > x ; mv x $f; done

for f in aac wav mp4 ; do LOCALE=C LANG=en_EN join -t$'\t' -j 2 original.$f.csv processed.$f.csv > joined.$f.csv ; done
