#!/bin/bash
# nb: only works on our specific ucb server setup
cd

for t in bampfa botgarden ucjeps pahma cinefiles
do 
  cd /var/www/$t
  if [[ ! -d "~/backup/$t/config" ]]; then
    mkdir -p ~/backup/$t/config
  fi
  cp -p config/*.cfg ~/backup/$t/config/
  cp -p config/*.csv ~/backup/$t/config/
  cp -p config/*.xml ~/backup/$t/config/
  cp -p config/*.json ~/backup/$t/config/
done
