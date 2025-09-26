#!/bin/bash
#    Written by:
#       Teren Sapp, teren@arista.com
#
#    Simple bash script for EOS to monitor a host and adjust static routes as needed
#    Edit the appropriate hosts (10.111.254.2 below) and adjust the routes
#    Save the script to /mnt/flash/routetracker.sh and make it executible with 'chmod +x /mnt/flash/routetracker.sh'
#    Finally, to run the script go into the EOS CLI and configure:
#
#    daemon routetracker
#      exec /mnt/flash/routetracker.sh
#      no shutdown
#

HOSTUP=Y
PingInterval=2
FailureCount=3
Count=0

while true; do
  for i in 10.111.254.2  # Replace with your monitoring IP
  do
    ping -c 1 -W 1 $i &> /dev/null
    PingResult=$?

    if [ $PingResult != "0" ]; then
      let "Count++"
      if [ "$HOSTUP" = "Y" ]; then
        if [ $Count = "$FailureCount" ]; then
          NOW=`/bin/date`
          echo "Host is down at" $NOW >> /mnt/flash/RouteTrack.log
          logger -p CRIT -t IPSLA "Host $i is up - Changing Routes"
          FastCli -p15 -c '
          enable
          conf term
          no ip route 10.111.254.2/32 10.111.1.1
          ip route 10.111.254.2/32 10.111.1.3'
          HOSTUP=N
        fi
      fi
    fi

    if [ $PingResult = "0" ]; then
      if [ "$HOSTUP" = "N" ]; then
        NOW=`/bin/date`
        echo "Host is up at" $NOW >> /mnt/flash/RouteTrack.log
        Count=0
        logger -p CRIT -t IPSLA "Host $i is down - Changing Routes"
        FastCli -p15 -c '
        enable
        conf term
        no ip route 10.111.254.2/32 10.111.1.3
        ip route 10.111.254.2/32 10.111.1.1'
        HOSTUP=Y
      fi
    fi
  done
  sleep $PingInterval
done
