YEAR=`date +%Y`
MONTH=`date +%m`

goaccess -o /var/www/static/stats_cinefiles_${YEAR}_${MONTH}.html --log-format=COMBINED --html-report-title="CineFiles Blacklight" /var/log/apache2/cinefiles-bampfa/${YEAR}/${YEAR}-${MONTH}-cinefiles-bampfa-ssl-access.log > /dev/null 2>&1
goaccess -o /var/www/static/stats_pahma_${YEAR}_${MONTH}.html --log-format=COMBINED --html-report-title="PAHMA Blacklight" /var/log/apache2/pahma/${YEAR}/${YEAR}-${MONTH}-pahma-ssl-access.log > /dev/null 2>&1
goaccess -o /var/www/static/stats_webapps_${YEAR}_${MONTH}.html --log-format=COMBINED --html-report-title="Webapps" /var/log/apache2/webapps/${YEAR}/${YEAR}-${MONTH}-webapps-ssl-access.log > /dev/null 2>&1

cp /var/www/static/stats_cinefiles_${YEAR}_${MONTH}.html /var/www/static/stats_cinefiles.html
cp /var/www/static/stats_pahma_${YEAR}_${MONTH}.html /var/www/static/stats_pahma.html
cp /var/www/static/stats_webapps_${YEAR}_${MONTH}.html /var/www/static/stats_webapps.html

