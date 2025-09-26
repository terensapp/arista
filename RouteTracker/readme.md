Simple bash script for EOS to monitor a host and adjust static routes as needed. Edit the appropriate hosts (10.111.254.2 below) and adjust the routes. Save the script to /mnt/flash/routetracker.sh and make it executible with 'chmod +x /mnt/flash/routetracker.sh'. Finally, to run the script go into the EOS CLI and configure:

daemon routetracker
  exec /mnt/flash/routetracker.sh
  no shutdown
