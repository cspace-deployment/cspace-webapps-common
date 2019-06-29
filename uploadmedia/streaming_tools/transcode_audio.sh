#
# helper script to trancode a .wav file to a 128kb/s .aac file
#
FFMPEG=/srv/nfs/media/ffmpeg/ffmpeg
echo `date` > $1.transcode.log
if [[ -e $1.wav ]]; then
    $FFMPEG -i $1.wav -b:a 128k $1_128k.aac >> $1.transcode.log 2>&1
else
    echo "ERROR: $1.wav does not exist" >> $1.transcode.log
fi
echo `date` >> $1.transcode.log
