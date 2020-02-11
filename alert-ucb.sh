#!/bin/bash
#
# a helper for making 'alerts' for the django webapps for ucb museums on rtl 'managed servers'
#
#set -x

WHOLE_LIST="bampfa botgarden cinefiles pahma ucjeps"

if [[ $# -eq 0 ]] ;
then
  echo
  echo "./alert-ucb.sh -h for help"
  echo
  exit 1
fi

while [[ $# -gt 0 ]] ;
do
  opt="$1";
  shift;
  case ${opt} in
    '-h' )
      echo
      echo "usage:"
      echo
      echo "to make an alert for all ucb museums"
      echo "./alert_ucb.sh -a -l 'Attention Please' -m 'Webapps coming down for upgrade at 10am'"
      echo
      echo "to alert particular museums, e.g. for pahma and cinefiles"
      echo "./alert_ucb.sh pahma -l 'Alert' -m 'PAHMA and CineFiles restarting shortly.' cinefiles"
      echo
      echo "nb: You CAN customize all this further if you really need to. See the README.md for details."
      echo
      echo "to clear alerts"
      echo "./alert_ucb.sh -a -c"
      echo "./alert_ucb.sh -c ucjeps bampfa"
      echo
      exit 0
    ;;
    '-a' )
      MUSEUMS=$WHOLE_LIST
    ;;
    '-l' )
      ALERT=$1 ; shift;
    ;;
    '-c' )
      CLEAR='clear' ;
    ;;
    '-m' )
      MESSAGE=$1 ; shift;
    ;;
    * )
    if [[ ! $MUSEUMS =~ .*$opt.* ]]
    then
        MUSEUMS="${MUSEUMS} $opt"
    fi
    ;;
  esac
done

SITE_DIR=cspace_django_site
BASE_DIR='..'

echo "****************************************************************************"
echo "Alert webapp users:"
echo "****************************************************************************"
if [[ $CLEAR != 'clear' ]]
then
    echo "label:   ${ALERT}"
    echo "message: ${MESSAGE}"
    echo "****************************************************************************"
fi

for t in $MUSEUMS
do
  if [[ $CLEAR == 'clear' ]]
  then
      rm ${BASE_DIR}/${t}/config/alert.cfg
      echo "Cleared alert for ${t}."
  else
      perl -pe "s/#ALERT#/${ALERT}/; s/#MESSAGE#/${MESSAGE}/;" ${BASE_DIR}/${t}/${SITE_DIR}/alert_template.cfg > ${BASE_DIR}/${t}/config/alert.cfg
      echo "Set alert for ${t}."
  fi
done
echo "Done."
echo "****************************************************************************"
