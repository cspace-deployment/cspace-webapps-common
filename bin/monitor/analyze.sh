#!/bin/bash
echo "<html><h2>Django Webapp Usage Summary</h2>" > summary.html
echo "<h4>`date`</h4>" >> summary.html
echo '<head>
    <link rel="stylesheet" type="text/css" href="css/reset.css">
    <link rel="stylesheet" type="text/css" href="css/base.css">
    <style>
    td {text-align: right;}
    </style>
</head>
<table>' >> summary.html
for t in bampfa botgarden cinefiles pahma ucjeps 
do
    echo "processing ${t} ..."
    ./genlogs.sh ${t}
    ./topblobs.sh ${t}
    ./bmulog.sh ${t}
done
cp *.bmu.log /var/www/static
gzip -f /var/www/static/*.bmu.log
./maketable.sh
grep -v facet combined.txt | perl -pe 's/^aa//;s/.start/:/;print "<tr><td>";s/\t/<td>/g;' >> summary.html
head -1 combined.txt |perl -pe 'print "<tr><td>";s/(\w+)/<a target="blobs" href="\1.blobs.html">top images<\/a>/g;s/\t/<td>/g;' >> summary.html
echo '</table><html>' >> summary.html
mv summary.html /var/www/static
