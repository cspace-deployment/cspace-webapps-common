#!/bin/bash
# tenant jobname parameterfile
# e.g.
# /var/www/ucjeps/uploadmedia/postblob.sh ucjeps 2015-11-10-09-09-09 ucjeps_Uploadmedia_Dev
#
/var/www/$1/uploadmedia/postblob.sh $1 $2 $3