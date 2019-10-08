''' This script is used for mapping the luns with the disks based on the disks count from hdb_sizes Json and create the physical volume groups
Example:  python3 disks.py S'''

import json
import os
import sys

def main():
    hdb_size=sys.argv[1]

    # below command will list the block devices and sort as per the lun numbers
    cmd="ls -ld /sys/block/sd*/device|grep 5:0|awk '{print $9,$11}'|awk -F '/' '{print $4,$8}'|awk -F ':' '{print $1 $4}'|sort -u -k2|awk '{print $1}'"
    disklist = os.popen(cmd).read().splitlines( )

    # reading the hana database sizes json file to get disks names and count
    hdb=open("/tmp/hdb_sizes.json")
    disks=json.loads(hdb.read())[hdb_size]['storage']

    #Initialize 2 variables x and y, x points to start of device count and until it reaches the count, y will build string by adding disks to diskstring varaible.
    y=0
    x=1

    # loop through disks dict and create the volume groups
    for disk in disks:
       if disk['name'] != 'os':
          diskstring=''

          # go through the disk count of hdb sizes json file and build string to create volume groups.
          for x in range(0, disk['count']):
             diskstring = diskstring +' '+ '/dev/'+disklist[y]+'1'
             y += 1;

          # create physical volume group
          vgcmd='vgcreate ' +'vg' + disk['name']  + ' ' + diskstring
          stream = os.popen(vgcmd)


if __name__=="__main__":
   main()
