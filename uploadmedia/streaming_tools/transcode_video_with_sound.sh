#
# helper script to transcode a .mp4 file to 2 files: a 500kp/s version with sound
#
FFMPEG=/srv/nfs/media/ffmpeg/ffmpeg
echo `date` > $1.transcode_with_sound.log
if [[ -e $1.mp4 ]]; then
    time $FFMPEG    -i $1.mp4 -c:v libx264 -b:v 500K  -b:a 64K    -movflags +faststart $1_500k_sound.mp4 >> $1.transcode_with_sound.log 2>&1 &
    #time $FFMPEG    -i $1.mp4 -c:v libx264 -b:v 500K          -an    -movflags +faststart $1_500k_silent.mp4 >> $1.transcode.log 2>&1 &
    #time $FFMPEG -y -i $1.mp4 -c:v libx264 -b:v 1200K -pass 1 -an -f mp4 /dev/null && \
    #     $FFMPEG    -i $1.mp4 -c:v libx264 -b:v 1200K -pass 2 -an -movflags +faststart $1_1200k_2pass_silent.mp4 >> $1.transcode.log 2>&1 &
    wait
else
    echo "ERROR: $1.mp4 does not exist" >> $1.transcode.log
fi
