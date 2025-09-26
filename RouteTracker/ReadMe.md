-----

## EOS Static Route Monitoring Script 🛰️

This is a simple bash script for Arista EOS designed to monitor a host and dynamically adjust static routes based on its availability.

-----

### Step 1: Create the Script and prepare the script

First, create your bash script. You'll need to **edit the IP addresses and routes** to match your specific network environment.

Save `routetracker.sh` to /mnt/flash/routetracker.sh

Make it executable with the `chmod` command:
    ```bash
    chmod +x /mnt/flash/routetracker.sh
    ```

### Step 2: Configure the EOS Daemon

Finally, go into the EOS command-line interface (CLI) and configure a daemon to run your script persistently.

```cli
enable
configure

daemon routetracker
   exec /mnt/flash/routetracker.sh
   no shutdown

end
```
