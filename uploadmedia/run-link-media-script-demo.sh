# how to run a couple of "helper scripts"
#
# link media records to objects
python linkMedia.py test-objs-media-link.csv /var/www/pahma/config/uploadmedia_batch.cfg
# create media records for existing blobs and link to objects
python createAndLinkMedia.py test-nomedia-jpegs-2012-cards.csv /var/www/pahma/config/uploadmedia_batch.cfg > cards.log 2>&1
