Create a python script pvaccesslist.py which lists all active EPICS PVAccess PVs.
To get a list of available PVAccess servers use pvlist program from EPICS without arguments. Output of the pvlist looks like this:

GUID 0x24397204572FF765D5482C55 version 2: tcp@[ 130.199.104.35:39303 192.168.50.202:39303 192.168.122.1:39303 ]
GUID 0xF8EC8C9CD38DBB6B9F0EA5C6 version 2: tcp@[ 130.199.104.35:5075 192.168.50.202:5075 192.168.122.1:5075 ]

For each line extract first IP_Port token which comes after 'tcp@['

For each IP_port execute 'pvlist IP_port' and write output to stdout.
