# python2 makeStreamingVersions.py jobnumber <file_metadata>
#
#
# e.g.
# time /var/www/pahma/uploadmedia/makeStreamingVersions.sh /srv/nfs/image_upload_cache_pahma/2015-11-10-09-09-09 500k.aac
#
# file_metadata is the characters to be inserted in the file name to distinguish the original file from the
# transcoded file.
#
# if the original file was "14-111.wav", and file_metadata is "500k.aac" then the job file will contain
# a file name of "14-111_500k.aac" (note that the extension is being replaced here...).
#
# if not supplied, the string "streaming" and the original extension will be used, e.g. "14-111_streaming.wav"
#
# all this script does is to make a suitable BMU input file (i.e. a ".step1.csv" file) for the given input file
# (which is assumed to be the output file from the job that uploaded the original media (i.e. a ".proccessed.csv" file
#
# It is intended that this script be run alongside (and after) the BMU is run, via cron, and after any transcoding
# is done.
#
# The transcoding is assumed to have been carried out by some other process, and the transcoded file need
# to be present in the same directory in which the various .csv file exist, i.e. the normal BMU temp directory
# (today, it is /srv/nsf/media/image_upload_cache_<tenant>
#

import sys, csv

if __name__ == "__main__":

    if len(sys.argv) == 2:

        # this should be the fully qualified name of the input file,
        # usually of the form "YYY-MM-DDD-HH-MM-SS.processed.csv"
        JOBFILE = sys.argv[1]
        FILENAME_EXTRA = "streaming"

    elif len(sys.argv) == 3:

        JOBFILE = sys.argv[1]
        if sys.argv[2] == "":
            FILENAME_EXTRA = "streaming"
        else:
            FILENAME_EXTRA = sys.argv[2]
    else:
        print
        print "usage: %s <jobname> <filename_extra>" % sys.argv[0]
        print "time python2 /var/www/pahma/uploadmedia/makeStreamingVersions.py /srv/nfs/image_upload_cache_pahma/2015-11-10-09-09-09 500k.aac"
        sys.exit(1)

    OUTPUTFILE = "%s_streaming.temp2.csv" % JOBFILE

    # make a new job ...by grepping the streaming files from the completed BMU job.
    INPUTFILE = "%s_streaming.temp1.csv" % JOBFILE
    ORIGINAL = "%s.original.csv" % JOBFILE

    print "MEDIA: job file (fully qualified path): %s" % JOBFILE
    print "MEDIA: filename extra:                  %s" % FILENAME_EXTRA

    records = []
    try:
        csvfile = csv.reader(open(JOBFILE, 'rb'), delimiter="|")
    except:
        print 'MEDIA: could not open (or perhaps find?) input file %s' % JOBFILE
        sys.exit()
    try:
        for row in csvfile:
            records.append(row)
    except:
        print 'MEDIA: could not read the rows of %s' % JOBFILE
        sys.exit()

    print 'MEDIA: %s data rows found in file %s' % (len(records) - 1, JOBFILE)
    if not 'original.csv' in JOBFILE:
        print "MEDIA: cowardly refusal to process a file that has not been already already processed: %s" % JOBFILE
        print "MEDIA: please rename your input file like 'xxxxx.original.csv'"
        sys.exit(1)
    outputFile = JOBFILE.replace('.original.csv', '-transcode.step1.csv')
    outputfh = csv.writer(open(outputFile, 'wb'), delimiter="|")

    # the first row of the file is a header
    columns = records[0]
    del records[0]
    outputfh.writerow(columns)

    for i, r in enumerate(records):
        media_filename = r[0]
        if not ('wav' in media_filename or 'mp4' in media_filename): continue
        for extension in 'wav mp4'.split(' '):
            media_filename = media_filename.replace('.%s' % extension, '_%s' % (FILENAME_EXTRA))
        r[0] = media_filename
        outputfh.writerow(r)

    print 'MEDIA: %s data rows written to file %s' % (i + 1, outputFile)
