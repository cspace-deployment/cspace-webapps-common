#!/bin/bash

YEAR=`date +%Y`
MONTH=`date +%m`

# we need to do this because somehow goaccess can't create them if they are not there... go figger.
for m in cinefiles pahma bampfa webapps
  do
    touch /var/www/static/stats_${m}_${YEAR}_${MONTH}.html
  done

goaccess -o /var/www/static/stats_cinefiles_${YEAR}_${MONTH}.html --log-format=COMBINED --html-report-title="CineFiles Blacklight" /var/log/apache2/cinefiles-bampfa/${YEAR}/${YEAR}-${MONTH}-cinefiles-bampfa-ssl-access.log > /dev/null 2>&1
goaccess -o /var/www/static/stats_pahma_${YEAR}_${MONTH}.html --log-format=COMBINED --html-report-title="PAHMA Blacklight" /var/log/apache2/portal/${YEAR}/${YEAR}-${MONTH}-portal-ssl-access.log > /dev/null 2>&1
goaccess -o /var/www/static/stats_bampfa_${YEAR}_${MONTH}.html --log-format=COMBINED --html-report-title="BAMPFA Blacklight" /var/log/apache2/collection/${YEAR}/${YEAR}-${MONTH}-collection-ssl-access.log > /dev/null 2>&1
goaccess -o /var/www/static/stats_webapps_${YEAR}_${MONTH}.html --log-format=COMBINED --html-report-title="Webapps" /var/log/apache2/webapps/${YEAR}/${YEAR}-${MONTH}-webapps-ssl-access.log > /dev/null 2>&1

cp /var/www/static/stats_cinefiles_${YEAR}_${MONTH}.html /var/www/static/stats_cinefiles.html
cp /var/www/static/stats_pahma_${YEAR}_${MONTH}.html /var/www/static/stats_pahma.html
cp /var/www/static/stats_bampfa_${YEAR}_${MONTH}.html /var/www/static/stats_bampfa.html
cp /var/www/static/stats_webapps_${YEAR}_${MONTH}.html /var/www/static/stats_webapps.html

# tidy up the mess left behind
rm -rf /tmp/goaccess*

