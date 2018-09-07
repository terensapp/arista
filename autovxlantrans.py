#!/usr/bin/python
#
# Copyright (c) 2015, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  - Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#  - Neither the name of Arista Networks nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Port auto-description
#
#    Version 1.0 4/3/2015
#    Written by: 
#       Teren Sapp, Arista Networks
#
#    Revision history:
#       1.0 - Initial version tested on EOS 4.14.4F 

"""
   DESCRIPTION
     This script automatically configures VLAN translation and
     mapping to the appropriate VNI. This allows the provisioning
     system to make a call to this script with the customer VLAN
     and the VNI and the script will automatically provision the
     local VLAN and map it to the appropriate VNI.

   INSTALLATION
     In order to install this script:
       - Copy the script to /mnt/flash
       - Enable the Command API interface:

            management api http-commands
              no shutdown

       - Change SWITCH, USERNAME, PASSWORD, CVLAN, CVNI, VLANRANGE at the top
         of the script to the ones appropriate for your
         installation. 

   USAGE

      - Usage: ./[scriptname] <cust_interface> <cust_vlan> <cust_vni>

   COMPATIBILITY
      This has been tested with EOS 4.14.4F using eAPI

   LIMITATIONS
      None known
"""

import sys
import json
from jsonrpclib import Server

def main(argv):

  #----------------------------------------------------------------
  # Configuration section
  #----------------------------------------------------------------
  SWITCH = '127.0.0.1'
  USERNAME = 'arista'
  PASSWORD = 'arista'
  VLANRANGE = [100,1000]
  #----------------------------------------------------------------

  try:
    CINT = argv[1]
    CVLAN = argv[2]
    CVNI = argv[3]
  except:
    sys.stderr.write("Usage: [scriptname] <cust_interface> <cust_vlan> <cust_vni>")
    exit(1)

  urlString = "https://{}:{}@{}/command-api".format(USERNAME,PASSWORD,SWITCH)
  switchReq = Server( urlString )
  try:
    showvlans = switchReq.runCmds( 1, ["show vlan"] )
  except:
    print "Could not communicate with switch. Please check eAPI configuration and verify URL"
    print "URL: " + urlString
    quit()
  
  existingvlans = []
 
  for VLAN in showvlans[0]['vlans']:
    existingvlans.append(VLAN)
 
  sortedvlans = sorted(existingvlans, key=int)
  candidatevlan = VLANRANGE[0] + 1

  # Find an open vlan within the range
  for VLAN in sortedvlans:
    VLAN = int(VLAN)
    # If we hit upper limit, exit out
    if candidatevlan >= VLANRANGE[1]:
      print "Error hit upper limit of VLAN range"  
      exit()

    newvlan = candidatevlan
    if VLAN == candidatevlan:
      candidatevlan = candidatevlan + 1

  newvlanstr = str(newvlan)
  try:
    confvlan = switchReq.runCmds( 1, ["enable","configure","vlan " + newvlanstr,"name AUTOVXLAN" + newvlanstr,"end"])
  except:
    print "Error provisioning vlan " + newvlanstr
    exit(1)
  try:
    confvxlan = switchReq.runCmds( 1,["enable","configure","interface vxlan1","vxlan vlan " + newvlanstr + " vni " + CVNI])
  except:
    noconfvlan = switchReq.runCmds( 1,["enable","configure","no vlan " + newvlanstr])
    print "Error provisioning mapping of VLAN " + newvlanstr + " to VNI " + CVNI
    exit(1)
  try:
    confmap = switchReq.runCmds( 1,["enable","configure","interface " + CINT,"switchport vlan mapping " + CVLAN + " " + newvlanstr])
  except:
    noconfvlan = switchReq.runCmds( 1,["enable","configure","no vlan " + newvlanstr])
    noconfvxlan = switchReq.runCmds( 1,["enable","configure","interface vxlan1","no vxlan vlan " + newvlanstr + " vni " + CVNI])
    print "Error provisioning vlan mapping on interface " + CINT
    exit(1)

  print "Successfully provisioned customer VLAN " + CVLAN + " to VNI " + CVNI + " on interface " + CINT

if __name__ == '__main__':
  main(sys.argv)
