#!/bin/bash
# nb: only works on our specific ucb server setup
cd

for t in bampfa botgarden ucjeps pahma cinefiles
do 
  cd /var/www/$t
  if [[ ! -d "~/backup/$t/config" ]]; then
    mkdir -p ~/backup/$t/config
  fi
  rsync -av --exclude alert.cfg config/ ~/backup/$t/config/
done
