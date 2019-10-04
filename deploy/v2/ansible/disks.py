#!/usr/src/Python-3.7
import json
import os
import sys
size=sys.argv[1]
cmd="ls -ld /sys/block/sd*/device|grep 5.0|awk '{print $9,$11}'|awk -F '/' '{print $4,$8}'|awk -F ':' '{print $1 $4}'|sort -u -k2|awk '{print $1}'"
stream = os.popen(cmd)
disk_list = stream.read()
disklist=disk_list.splitlines( )
jsonFile=open("/tmp/hdb_sizes.json")
jsonString=jsonFile.read()
data=json.loads(jsonString)
disks=data[size]['storage']
y=0;
x=1;
for dict in disks:
     dk_name=dict['name']
     dk_count=dict['count']
     if dict['name'] != 'os':
        diskstring=''
        for x in range(0, dk_count):
            diskstring = diskstring +' '+ '/dev/'+disklist[y]+'1'
            y += 1;
        vgcmd='vgcreate ' +'vg' + dk_name  + ' ' + diskstring
        stream = os.popen(vgcmd)
        print (stream)
#print (mydict)
