#!/bin/bash

HTML_FILE=/var/www/static/metrics.html

cd /var/www/static

cat > ${HTML_FILE}<<HERE
<html>
<h3>Some metrics for CSpace@UCB</h3>
<p><i>Sorry, for most of them you'll have to guess what they are...</i></p>
<ul>
<li><a target="metrics" href="corestats.html">Summary stats on museum database contents (record counts)</a></li>
<li><a target="metrics" href="summary.html">Django webapp use (both public and internal)</a></li>
<li><a target="metrics" href="webappuse.html">Legacy report on Toolbox webapp use (until Nov 2019)</a></li>
<li><a target="metrics" href="bmu_stats.html">Graphs of BMU usage over time</a></li>
</ul>
HERE

for m in bampfa botgarden cinefiles pahma ucjeps
  do
    echo "<h3>${m}</h3><ul>" >> ${HTML_FILE}
    for f in *${m}*.html
      do
        echo "<li><a target="metrics" href="${f}">${f}</a></li>" >> ${HTML_FILE}
      done
    echo "</ul>" >> ${HTML_FILE}
  done
echo '</html>' >> ${HTML_FILE}
