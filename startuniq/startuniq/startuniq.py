#!/usr/bin/env python3
"""Start a remote program only if it is not already running.
If it is running, ask the user whether to kill it or not.
Usage:
    startuniq.py -s RemoteHost Program [ProgramArgs ...]
"""
__version__ = 'v0.0.3 2026-08-11'# 

import time
import argparse
import shlex
import subprocess
import sys
import socket
import tkinter as tk

Hostname = socket.gethostname()
print(f"Hostname: {Hostname}")

class KillStartDialog:
    def __init__(self, parent, text):
        self.top = tk.Toplevel(parent)
        self.top.title('Alert')
        self.result = None

        # Add label
        label = tk.Label(self.top, text=text)
        label.pack(padx=20, pady=20)

        # Add Kill button
        btn_kill = tk.Button(self.top, text="Kill", command=self.on_kill, fg="red")
        btn_kill.pack(side=tk.LEFT, padx=20, pady=10)

        # Add Start button
        btn_start = tk.Button(self.top, text="Start anyway", command=self.on_start)
        btn_start.pack(side=tk.RIGHT, padx=20, pady=10)

        # Make window modal
        self.top.grab_set()
        
    def on_kill(self):
        self.result = "kill"
        self.top.destroy()
        
    def on_start(self):
        self.result = "start"
        self.top.destroy()

def run_ssh(host: str, remote_cmd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["ssh", host, remote_cmd],
        text=True,
        capture_output=True,
        check=False,
    )

def kill_remote_program(host: str, program_name: str) -> bool:
    """Kill remote program by exact full command line match."""
    kill_cmd = f"pkill -f {shlex.quote(program_name)}"
    #print(f"Attempting to kill remote program on {host}: {kill_cmd}")
    result = run_ssh(host, kill_cmd)
    print(f'Executed on {host}: {kill_cmd}')

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start remote program uniquely",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=__version__)
    parser.add_argument("-S", "--sleep", default=0.1, type=float, help=
      'delay')
    parser.add_argument("-s", "--server", default=Hostname, help="Remote host")
    parser.add_argument("-p", "--process", default=None, help="Process name to check (default: full command line)")
    parser.add_argument("program", nargs='*', help="Program to start")
    args = parser.parse_args(argv)

    if not args.program:
        parser.error("Program is required")

    return args

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    host = args.server
    program_argv = args.program
    process_name = args.process if args.process else ' '.join(program_argv)
    check_cmd = f"pgrep -c -f {shlex.quote(process_name)}"

    # Run the check command on the remote host
    check_result = run_ssh(host, check_cmd)
    time.sleep(args.sleep)
    #print(f'check_result: {check_result}')
    stdout = check_result.stdout.strip()
    #print(f"Check result for {check_cmd}: returncode={check_result.returncode}, stdout={stdout}, stderr={check_result.stderr.strip()}")
    if int(stdout) > 1:
        txt = (f"'{process_name}' is already running on {host}.\n\n"
        "Press Kill to terminate it, or Start to start it.")
        
        root = tk.Tk()
        root.withdraw() # Hide main window for test

        dialog = KillStartDialog(root, txt)
        root.wait_window(dialog.top)
        #print("User chose:", dialog.result)
        if dialog.result == 'kill':
            kill_remote_program(host, process_name)
            return 1

    if check_result.returncode not in (0, 1):
        print(
            f"Failed to check remote process on {host}: {check_result.stderr.strip()}",
            file=sys.stderr,
        )
        return 2

    # Start the program in the background on the remote host
    launch_cmd = " ".join(shlex.quote(part) for part in program_argv)
    start_cmd = f"{launch_cmd}&"
    start_result = subprocess.Popen(["ssh", host, start_cmd], text=True,)

    #print(f"Start result: returncode={start_result.returncode}, stdout={start_result.stdout.strip()}, stderr={start_result.stderr.strip()}")
    #print(f"Start result: returncode={start_result.returncode}")
    print(f"Started on {host}: {' '.join(program_argv)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
