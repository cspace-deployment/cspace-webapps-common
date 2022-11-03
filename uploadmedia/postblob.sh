#!/bin/bash

# these better be here!
source ~/.profile
source ${HOME}/venv/bin/activate

# three arguments required:
#
# postblob.sh tenant jobnumber configfilewithoutcfgextension
#
# e.g.
# time /var/www/ucjeps/uploadmedia/postblob.sh ucjeps 2015-11-10-09-09-09 ucjeps_Uploadmedia_Dev

TENANT=$1
RUNDIR="/var/www/${TENANT}/uploadmedia"
UPLOADSCRIPT="$RUNDIR/uploadMedia.py"

CONFIGDIR="/var/www/${TENANT}/config"
MEDIACONFIG="$CONFIGDIR/$3"

# this should be the fully qualified name of the input file, up to ".step1.csv"
JOB=$2
IMGDIR=$(dirname $2)

# claim this job...by renaming the input file
mv $JOB.step1.csv $JOB.inprogress.csv
INPUTFILE=$JOB.inprogress.csv
OUTPUTFILE=$JOB.step3.csv
LOGDIR=$IMGDIR
CURLLOG="$LOGDIR/curl.log"
CURLOUT="$LOGDIR/curl.out"
TRACELOG="$JOB.trace.log"

rm -f $OUTPUTFILE

TRACE=2

function trace()
{
   tdate=`date "+%Y-%m-%d %H:%M:%S"`
   [ "$TRACE" -eq 1 ] && echo "TRACE: $1"
   [ "$TRACE" -eq 2 ] && echo "TRACE: [$JOB : $tdate ] $1" >> $TRACELOG
   echo "$1"
}

trace "**** START OF RUN ******************** `date` **************************"
trace "output file: $OUTPUTFILE"

if [ ! -f "$INPUTFILE" ]
then
    trace "Missing input file: $INPUTFILE"
    exit
else
    trace "input file: $INPUTFILE"
fi
trace ">>>>>>>>>>>>>>> Starting Blob, Media, and Relation record creation process: `date` "
# handle .CR2 files: convert them to TIFs and JPGs, and upload then upload the JPGs 'as usual'
# save the TIFs back into s3 for ingestion into Merritt
# first, get a list of all the CR2s in the job
grep -i '\.CR2' $INPUTFILE | cut -f1 -d"|" > CR2file
# convert them all
for CR2 in `cat CR2file`
  do
    F=$(echo "$CR2" | sed "s/\.CR2/_CR2/i")
    # fetch the CR2 from S3
    echo "${RUNDIR}/cps3.sh \"$CR2\" ucjeps from" >> $TRACELOG
    ${RUNDIR}/cps3.sh "$CR2" ucjeps from >> $TRACELOG 2>&1
    # make a jpg and a tif for each cr2
    for FORMAT in JPG TIF
    do
      echo "converting ${CR2} to ${F}.${FORMAT}" >> $TRACELOG
      convert -verbose "/tmp/${CR2}" "/tmp/${F}.${FORMAT}" >> $TRACELOG 2>&1
      # put the converted file back into S3
      echo "${RUNDIR}/cps3.sh \"${F}.${FORMAT}\" ucjeps to" >> $TRACELOG
      ${RUNDIR}/cps3.sh "${F}.${FORMAT}" ucjeps to >> $TRACELOG 2>&1
    done
  rm "/tmp/${CR2}"
done
# change the file names in the bmu job file so that it will upload the JPGs
perl -i -pe 's/\.CR2/_CR2.JPG/i' $INPUTFILE
# make a copy of the input file suitable for input to the merritt archiving system
perl -pe 's/\.CR2/_CR2.TIF/i' $INPUTFILE > $JOB.archive.csv

trace "python $UPLOADSCRIPT $INPUTFILE $MEDIACONFIG >> $TRACELOG"
python $UPLOADSCRIPT $INPUTFILE $MEDIACONFIG >> $TRACELOG 2>&1
trace "Media record and relations created."

mv $INPUTFILE $JOB.original.csv
mv $JOB.step3.csv $JOB.processed.csv

rm CR2file

trace "**** END OF RUN ******************** `date` **************************"
