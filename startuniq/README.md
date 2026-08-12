# startuniq

`startuniq` starts a program only when an equivalent process is not already running.
If it detects a running instance, it shows a small dialog that lets you:

- **Kill** existing instance(s), or
- **Start anyway**

It works for both:

- **remote hosts** (via SSH), and
- **localhost** (runs directly, no SSH)

Useful for single-instance tools such as Firefox, VS Code, Zim, Phoebus, and similar apps.

## Requirements

- Python 3.7+
- Linux/Unix-like system
- `pgrep` and `pkill` available on target host
- Tkinter (for the confirmation dialog)

## Installation

`pip install startuniq`

Or from this folder:

`pip install .`


## Usage

`python -m startuniq -s HOST [-p PROCESS_PATTERN] PROGRAM [PROGRAM_ARGS ...]`

### Arguments

- `-s`, `--server`: target host (default: `localhost`)
- `-p`, `--process`: process match pattern for `pgrep -f`
	- if omitted, the full command line (`PROGRAM + args`) is used
- `PROGRAM [PROGRAM_ARGS ...]`: command to launch

## Examples

Start Firefox on remote host:

`python -m startuniq -s myhost firefox`

Start VS Code locally (no SSH):

`python -m startuniq code /path/to/project`

## Behavior summary

1. Checks process count using `pgrep -c -f`.
2. If already running, shows **Kill / Start anyway** dialog.
3. If not running (or user chooses Start anyway), launches the program.

## Notes

- For remote hosts, command checks and launches happen through SSH.
- For `localhost`, checks and launches run directly on the local machine.

