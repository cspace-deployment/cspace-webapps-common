# NB: BAM no longer uses the BMU: derivatives from Piction are pushed to CSpace
for t in botgarden cinefiles pahma ucjeps; do python3 /var/www/$t/uploadmedia/checkRuns.py /cspace/bmu/$t jobs summary $t | mail -r "cspace-support@lists.berkeley.edu" -s "recent $t BMU jobs" jblowe@berkeley.edu,rjaffe@berkeley.edu; done
for t in botgarden cinefiles pahma ucjeps; do python3 /var/www/$t/uploadmedia/checkRuns.py /cspace/bmu/$t jobs summary $t > /var/www/static/${t}.nightly.report.txt ; done
# bmu 'usage graphs': plots of nightly bmu uploads
bash -l -c 'python3 /var/www/pahma/uploadmedia/bmu-nightly-2022-concise.py > /dev/null'
python3 /var/www/pahma/uploadmedia/checkRuns.py /cspace/bmu/pahma jobs summary pahma | mail -r "cspace-support@lists.berkeley.edu" -s "recent PAHMA BMU jobs" pahma-cspace-bmu@lists.berkeley.edu > /dev/null 2>&1
python3 /var/www/ucjeps/uploadmedia/checkRuns.py /cspace/bmu/ucjeps jobs summary ucjeps | mail -r "cspace-support@lists.berkeley.edu" -s "recent UCJEPS BMU jobs" ucjeps-it@berkeley.edu > /dev/null 2>&1
python3 /var/www/cinefiles/uploadmedia/checkRuns.py /cspace/bmu/cinefiles jobs summary cinefiles | mail -r "cspace-support@lists.berkeley.edu" -s "recent Cinefiles BMU jobs" bampfacspaceuploader@lists.berkeley.edu > /dev/null 2>&1
python3 /var/www/botgarden/uploadmedia/checkRuns.py /cspace/bmu/botgarden jobs summary botgarden | mail -r "cspace-support@lists.berkeley.edu" -s "recent UCBG BMU jobs" ucbg-cspace-bmu@lists.berkeley.edu > /dev/null 2>&1
