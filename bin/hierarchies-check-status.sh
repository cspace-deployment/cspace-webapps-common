#!/bin/bash

source ${HOME}/pipeline-config.sh

cd ${HOME}/cspace-utils-ucb/pahma
psql -h localhost -p 54321 -U pahma -d pahma_domain_pahma -f checkstatus.sql | mail -r cspace-support@lists.berkeley.edu -s "hierarchies refresh" "${PAHMA_CONTACT}"
