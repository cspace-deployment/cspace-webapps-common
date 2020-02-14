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
      echo "to see what alerts are set"
      echo "./alert_ucb.sh -a -s"
      echo "./alert_ucb.sh -s ucjeps bampfa"
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
      ACTION='clear' ;
    ;;
    '-s' )
      ACTION='show' ;
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
BASE_DIR='/var/www'

echo "****************************************************************************"
echo "Alert webapp users:"
echo "****************************************************************************"
if [[ $ACTION != 'clear' && $ACTION != 'show' ]]
then
    echo "label:   ${ALERT}"
    echo "message: ${MESSAGE}"
    echo "****************************************************************************"
fi

for t in $MUSEUMS
do
  if [[ $ACTION == 'clear' ]]
  then
      rm -f ${BASE_DIR}/${t}/config/alert.cfg
      echo "Cleared alert for ${t}."
  elif [[ $ACTION == 'show' ]]
  then
      echo
      echo "Alert for ${t}:"
      if [[ -f ${BASE_DIR}/${t}/config/alert.cfg ]]
      then
          cat ${BASE_DIR}/${t}/config/alert.cfg
      else
          echo "No alert set"
      fi
  else
      perl -pe "s/#ALERT#/${ALERT}/; s/#MESSAGE#/${MESSAGE}/;" ${BASE_DIR}/${t}/${SITE_DIR}/alert_template.cfg > ${BASE_DIR}/${t}/config/alert.cfg
      echo "Set alert for ${t}."
  fi
done
echo "****************************************************************************"
echo "Done."
echo "****************************************************************************"
