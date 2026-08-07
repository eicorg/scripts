#!/usr/bin/env python3
"""Start a remote program only if it is not already running.
If it is running, ask the user whether to kill it or not.
Usage:
    startuniq.py -s RemoteHost Program [ProgramArgs ...]
"""
__version__ = 'v0.0.2 2026-08-07'# do not use pgrep -x.

import argparse
import shlex
import subprocess
import sys
import socket
import tkinter as tk

Hostname = socket.gethostname()
print(f"Hostname: {Hostname}")

def show_running_dialog(message: str) -> bool:
    """Show a dialog with Kill/Cancel. Return True when Kill is pressed."""
    try:

        result = {"kill": False}

        root = tk.Tk()
        root.title("Program already running")
        root.attributes("-topmost", True)
        root.resizable(False, False)

        frame = tk.Frame(root, padx=16, pady=12)
        frame.pack(fill=tk.BOTH, expand=True)

        label = tk.Label(frame, text=message, justify=tk.LEFT, wraplength=420)
        label.pack(anchor="w", pady=(0, 12))

        buttons = tk.Frame(frame)
        buttons.pack(anchor="e")

        def on_kill() -> None:
            result["kill"] = True
            root.destroy()

        def on_cancel() -> None:
            result["kill"] = False
            root.destroy()

        tk.Button(buttons, text="Kill", width=10, command=on_kill).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(buttons, text="Cancel", width=10, command=on_cancel).pack(side=tk.LEFT)

        root.protocol("WM_DELETE_WINDOW", on_cancel)
        root.mainloop()
        return result["kill"]
    except Exception:
        print(message, file=sys.stderr)
        try:
            answer = input("Kill remote process? [y/N]: ").strip().lower()
            return answer in ("y", "yes")
        except Exception:
            return False

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
    if result.returncode == 0:
        print(f"Killed on {host}: {program_name}")
        return True

    if result.returncode == 1:
        print(f"No matching process found to kill on {host}: {program_name}")
        return False

    print(
        f"Failed to kill remote process on {host}: {result.stderr.strip()}",
        file=sys.stderr,
    )
    return False

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start remote program uniquely",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=__version__)
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
    stdout = check_result.stdout.strip()
    #print(f"Check result for {check_cmd}: returncode={check_result.returncode}, stdout={stdout}, stderr={check_result.stderr.strip()}")
    if int(stdout) > 1:
        do_kill = show_running_dialog(
            f"'{process_name}' is already running on {host}.\n\n"
            "Press Kill to terminate it, or Cancel to exit."
        )
        if do_kill:
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
    #print(f"Starting program on {host}: {start_cmd}")
    start_result = subprocess.Popen(["ssh", host, start_cmd], text=True,)

    #print(f"Start result: returncode={start_result.returncode}, stdout={start_result.stdout.strip()}, stderr={start_result.stderr.strip()}")
    print(f"Start result: returncode={start_result.returncode}")

    print(f"Started on {host}: {' '.join(program_argv)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
