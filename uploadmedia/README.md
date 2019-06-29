## Deploying and Configuring the Bulk Media Uploader (BMU)

This webapp and its associated "batch processes" provide a means to upload multiple media files
in one fell swoop and (optionally, provided the media files are appropriately names) relate the media
files to object records

_Caveat utilizator!_ This is all fresh and wet behind the gills!

The BMU uses the "standard" multi-file upload capability provided by most
HTTP client framework to allow users to upload batches of images and
provide associated metadata. 

BMU has two components, one online, one "offline":

* A django webapp that allows users to upload media (via the
  "standard" Django file upload components) and metadata (via a
  combination of form input and metadata in the EXIF data in the
  image.)

* A batch component consisting of shell and python scripts, which takes
  the uploaded images and metadata and "ingests" them into CSpace.

To deploy it on an IS&T Unix Team-managed server, (A RHEL6 VM, e.g. cspace-prod.cspace.berkeley.edu):

### WEBAPP COMPONENT:

* Clone this repo and install and configure the Django
  webapp(s), including this one, "as usual" (see the README.md for the Django project, one level up).

  In particular, edit ```uploadmedia.cfg``` to point to the temporary cache,
  which you will need to create and perhaps set permissions and SELinux tags for
  (this directory needs to be writable by the Apache server, and at UCB, the WSGI
  process which the webapps run under is owned by the application owner "app_webapps"). 
 
  `/tmp` is usually a good place to put this cache. At UCB, the caches are all
  of the form `/tmp/image_upload_cache_<name of tenant>`
 
  Record the full path in `[files]` section of `uploadmedia.cfg`

  e.g.
```
  [files]
  directory         = /tmp/image_upload_cache_pahma
```

   `uploadmedia.cfg` is also where you will configure tenant specific media handling
   options. These can get pretty complicated, so study the existing UCB
   configurations and associated JIRAs to understand how they work. 
   
   Alas, the ability to configure dropdowns with specific attributes and values 
   is limited, and the BMU code itself contains a number of tenant-specific
   code blocks that you may need to modify to get the effect you want.

### BATCH COMPONENT:

* Follow the following steps to configure the batch component to run in
  the environment you are using: the batch component relies on cron or
  something similar to run, and has a number of expectations (dependencies)
  about where things are located and what they are named.
  Sorry it is so complicated, someday we'll make it more robust.

* Copy (from e.g. `django_example_config`) the appropriate `.cfg` file to a new config file in this directory
  (i.e. uploadmedia/) or create a new one. Edit the configuration for use by the the batch script `postblob.sh`,
  below.

  e.g.

```
  cp ~/django_example_config/pahma/pahma_Uploadmedia_Dev.cfg pahma_Uploadmedia_Dev.cfg
  vi pahma_Uploadmedia_Dev.cfg
```

* Copy `postblobRevised.sh` to `postblob.sh` in this directory. (NB `postblobviaHttp.sh` and `postblobviaFile.sh` are
  legacy versions of this script, but they might be useful as they illustrate other ways to upload Blobs)

```
  cp postblobRevised.sh postblob.sh
```

* This batch script does not require editing any more: all parameters are passed on the command line.

* (NB: `postblobviaFile.sh` can be used if this webapp is running on the same server
  as the CSpace deployment it address -- and therefore can use the
  somewhat more efficient "direct file move" CSpace blob upload
  facility). `postblobviaHttp.sh` must be used if the blob is to be POSTed over HTTP to a
  CSpace server.

* Ensure that the temporary cache for images and intermediate files is
  present and properly configured with appropriate permissions. For the
  online portion, the current setting is /tmp/image_upload_cache_{TENANT}.

* Alas, there is no way to test this webapp except to upload some
  media files.

* There are some helper scripts: "runJob.sh" runs a single job from
  the command line. "runHelpers.sh" attempts to find problem media and
  create jobs to re-load/re-link them. See below.

* The batch portion of the system is run via cron, and apache owns the
  uploaded files so it has to be run as use apache.  And there is a
  script that reports on the status of uploads that runs via cron as
  well.

  Here is the part of the current crontab for app_webapps on cspace-prod.cspace, where the batch process run periodically:

```
(venv)[app_webapps@cspace-prod-01 ~]$ crontab  -l

# email bmu job stats
10  5  * * * perl /var/www/pahma/uploadmedia/checkRuns.pl jobs | expand -12 | mail -s "recent BMU jobs" pahma-cspace@berkeley.edu > /dev/null 2>&1
# run UCJEPS BMU (one minute after the hour, noon and 8pm)
1 12,20 * * * shopt -s nullglob; for f in /tmp/image_upload_cache_ucjeps/*.step1.csv; do f=$(echo $f | sed -e 's/\.step1.csv//') ; time /var/www/ucjeps/uploadmedia/postblob.sh ucjeps $f ucjeps_Uploadmedia_Prod >> /tmp/image_upload_cache_ucjeps/batches.log; done
```

A few more details on the batch process:

The "batch process", which runs nightly (or more frequently) as a cron job as shown above,
is really just a small bash script wrapper around a python script
(uploadMedia.py) that does the heavy lifting. The heavy lifting is as
follows:

* The webapp creates metadata files (*.step1.csv) in a tmp/ directory.
  These point to the media files that were uploaded via the webapp to
  the same tmp/ directory. (the directory is a config parameter to the
  webapps, and for PAHMA it currently points to
  dev.space:/tmp/image_upload)

* Every night, cron globs all the *.step1.csv files together, passes
  the list of files to uploadMedia.py, which POSTs to the Blob, Media and
  Relations services to create Blobs and Media records and connect them to the
  corresponding Collectionobjects (if needed).

* In more detail:

- the shell script postblobs.sh process a file (*.step1.csv) which is a
  list of image filenames and metadata. It calls the python script uploadMedia.py
  which POSTs to the Blob service to create blobs, then POSTs to the
  Media service, outputting a file *.step3.csv for every successful
  Media (and making bidirectional Relation if collectionobjects are involved.)

- Finally the bash script renames the *.step*.csv file to
  *.original.csv and *.processed.csv. This creates a trace for
  verification and prevents the images from being reprocessed the next
  time the cron job runs.

As an aside, note that this tmp/ directory is cleaned up by a script cleanBMUtempdir.sh,
which deletes files older than 48 hours -- i.e. there is a 2 day cache
of images load, in case something needs to be recovered or rerun. The various
"control files" (.csv and .log) are kept around forever.

Finally, there are a few other (very speculative!) scripts that are
used for reporting and maintenance:

* bulkmediaupload.sh - this runs a single *.step1.csv file; it can be used 
to run a specific upload "by hand" from the command line.

* checkObj.pl - this script checks Blobs uploaded vs. Media created; it
is used by the very rickety "runHelpers.sh" script below to report on
problem records.

* checkRuns.pl - this script creates some reports on BMU activity:
number of jobs and their status, lists of images and the CSIDs, finds
problem data (missing images, duplicates, etc.)

* runHelpers.sh - matches CSIDs loaded with log files, to find
discrepancies between what is in the database and what seems to have
been uploaded. No longer works due to schema changes in the Solr
datasource, which it uses to find Blob CSIDs.

* runJob.sh - like bulkmediaupload.sh, but does not cleanup/rename
intermediate files.

* verifyObjectsAndMedia.sh - somewhat scary script to make a list of
imagefile names and object numbers...

### RUNNING THE BMU FROM THE COMMAND LINE

Once it is installed, the BMU can be invoked on the command line on one of the manage servers as follows:

```
$ ssh cspace-dev.cspace.berkeley.edu
(venv)[app_webapps@cspace-dev-01 ~]$ sudo su - app_webapps
(venv)[app_webapps@cspace-dev-01 ~]$ /var/www/bampfa/uploadmedia/postblob.sh /tmp/image_upload_cache_bampfa/xxxxxx
```

Provided you have a metadata file named "xxxxxx.step1.csv" in the pwd with an appropriate header, you should get some results.

Here is an example header (for PAHMA), with some sample data:

name (i.e. field name)
size (can be null)
objectnumber
date (can be null)
creator (refname)
contributor
rightsholder (refname)

e.g.

1-4673_2014_10_13at09_18_25.JPG

4416952

1-4673

2014:10:13 09:18:25

urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7652)'A Person Name'

Trinity Miller

urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(8107)'Phoebe A. Hearst Museum of Anthropology'

NB: the image files mentioned in this file must also be present in this same directory.


## UCB-SPECIFIC FEATURES

There are a number of UCB-specific customizations incorporated directly into the code. These
are conditionally executed depending on the configuration provided (in the config file)

Some of these are handled as part of the initial upload (i.e. online, by the BMU webapp itself). Others
are implemented in the batch script ```uploadMedia.py``` which does the actual ingestion, usual at night
via ```cron```.

Here's a list:

* For PAHMA, the "set primary" batch job is run after each media record is created; this ensures that
the last uploaded record in a sequence of records for an object becomes the primary. This convention allows
PAHMA staff to determine which media record will become primary without having to login to the regular UI,
find the media record, and mark it as primary by hand.
* For botgarden, media file names containing "_label" are assigned an image number of "999" so that they are displayed at the end of a sequence of images.
Also, the contributors initials are extracted from the file name and used to look up the refName of contributor
(supplied in the configuration file) so that a reference to their authority record can be inserted into the
database.
* For CineFiles, a number of fields are extracted from the EXIF data and added to media records.
* The different tenants have different conventions for handling image sequencing. These are all handled by
custom code in the batch script.
* The different tenants have different object number patterns. While in general the BMU uses the initial characters
up to an underscore to look up as the object number, more complex parsing of filenames is often required.
This is performed during upload by code in ```getNumber.py```.

