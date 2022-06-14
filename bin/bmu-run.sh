#!/bin/bash

source ${HOME}/pipeline-config.sh

for t in bampfa botgarden cinefiles pahma ucjeps; do
  shopt -s nullglob ; for f in /cspace/bmu/${t}/*.step1.csv
  do f=$(echo $f | sed -e "s/\.step1.csv//")
    time /var/www/${t}/uploadmedia/postblob.sh ${t} $f uploadmedia_batch  >> /cspace/bmu/${t}/batches.log 2>&1
  done
done
