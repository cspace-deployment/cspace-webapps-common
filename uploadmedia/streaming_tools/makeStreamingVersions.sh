#!/bin/bash

# makeStreamingVersions.sh jobnumber
#
# e.g.
# time /var/www/ucjeps/uploadmedia/makeStreamingVersions.sh /tmp/image_upload_cache_ucjeps/2015-11-10-09-09-09
FFMPEG="cp"

# this should be the fully qualified name of the input file, up to ".original.csv"
JOB="$1"
IMGDIR=$(dirname "$1")
TRACELOG="$JOB-streaming.trace.log"
OUTPUTFILE=$JOB-streaming.temp2.csv
LOGDIR=$IMGDIR

rm -f $OUTPUTFILE
rm -f $TRACELOG

TRACE=2
function trace()
{
   tdate=`date "+%Y-%m-%d %H:%M:%S"`
   [ "$TRACE" -eq 1 ] && echo "TRACE: $1"
   [ "$TRACE" -eq 2 ] && echo "TRACE: [$JOB : $tdate ] $1" >> $TRACELOG
}

# make a new job ...by grepping the streaming files from the completed BMU job.
INPUTFILE=$JOB-streaming.temp1.csv
grep -v -i "\.jpg" $JOB.original.csv | grep -v -i "\.tif" > $INPUTFILE

if [ "1" == $(wc -l < "$INPUTFILE") ]
then
    rm $INPUTFILE
    echo "no streaming media files in $INPUTFILE"
    exit
fi

trace "**** START OF RUN ******************** `date` **************************"

if [ ! -f "$INPUTFILE" ]
then
    trace "Missing input file: $INPUTFILE"
    echo "Missing input file: $INPUTFILE exiting..."
    exit
else
    trace "input file:  $INPUTFILE"
fi
trace "output file: $OUTPUTFILE"

while IFS='|' read -r FILENAME size objectnumber digitizedDate creator contributor rightsholder imagenumber handling approvedforweb copyright imagetype type source description
do
  # 'name' is the column header for the filename...
  if [ ! $FILENAME == "name" ]
  then
      FILEPATH="$IMGDIR/$FILENAME"
      trace "$objectnumber | $digitizedDate | $FILENAME"

      if [ ! -f "$FILEPATH" ]
      then
        trace "Missing file: $FILEPATH"
        continue
      fi

      TRANSCODED_FILE=$(echo $FILENAME | sed -e 's/\./_transcoded./')
      TRANSCODED_FILEPATH="$IMGDIR/$TRANSCODED_FILE"

      trace "$FFMPEG $FILEPATH $TRANSCODED_FILEPATH >> $TRACELOG"
      $FFMPEG $FILEPATH $TRANSCODED_FILEPATH >> $TRACELOG 2>&1
  else
      TRANSCODED_FILE=$FILENAME
  fi

  echo "$TRANSCODED_FILE|$size|$objectnumber|$digitizedDate|$creator|$contributor|$rightsholder|$imagenumber|$handling|$approvedforweb|$copyright|$imagetype|$type|$source|$description" >>  $OUTPUTFILE
done < $INPUTFILE

trace "Servable version(s) created and ready for ingestion."

mv $OUTPUTFILE $JOB-streaming.step1.csv
rm $INPUTFILE

trace "**** END OF RUN ******************** `date` **************************"
