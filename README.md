# scripts
Various scripts

- [pvaccesslist:](https://github.com/eicorg/scripts/tree/main/pvaccesslist)
List all active EPICS PVAccess PVs.
Discovers servers using `pvlist`, extracts the first `ip:port` token after `tcp@[`,
then runs `pvlist <ip:port>` for each server and writes results to stdout.

- [startuniq:](https://github.com/eicorg/scripts/tree/main/startuniq)
Start program on a remote/local host only if it is not already running.
If it is running, ask the user whether to kill it or not.

