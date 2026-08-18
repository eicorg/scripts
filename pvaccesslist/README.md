# pvaccesslist

List all active EPICS PVAccess PVs.

The script works as follows:
1. Runs `pvlist` with no arguments to discover PVAccess servers.
2. From each discovered line, extracts the first `ip:port` token after `tcp@[`.
3. Runs `pvlist <ip:port>` for each extracted endpoint.
4. Writes command output to stdout.

## Requirements

- EPICS `pvlist` must be available in `PATH`.
- Python 3.7+

## Usage

- Show help:
	- `python3 -m pvaccesslist.pvaccesslist -h`
- List PVs to terminal:
	- `python3 -m pvaccesslist.pvaccesslist`
- Save PV list to file:
	- `python3 -m pvaccesslist.pvaccesslist > pvs.txt`

## Notes

- If `pvlist` is missing, the script exits with an error message.
- Server discovery diagnostics are printed to stderr; PV names are printed to stdout.
