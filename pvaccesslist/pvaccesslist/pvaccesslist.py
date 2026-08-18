#!/usr/bin/env python3
"""List active EPICS PVAccess PVs by querying discovered PVA servers."""
__version__ = 'v0.0.1 2026-08-18'# created
import re
import subprocess
import sys

FIRST_TCP_ENDPOINT_RE = re.compile(r"tcp@\[\s*([^\s\]]+)")

def print_usage() -> None:
    """Print usage information."""
    print(
        "Description:\n"
        "  List active EPICS PVAccess PVs by discovering PVA servers with 'pvlist'\n"
        "  and running 'pvlist <ip:port>' for each discovered server.\n"
        "Usage:\n"
        "  pvaccesslist.py\n"
        "  pvaccesslist.py > pvs.txt\n"
        "  python3 -m pvaccesslist.pvaccesslist\n"
    )

def run_pvlist(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run `pvlist` and return completed process with captured text output."""
    try:
        return subprocess.run(
            ["pvlist", *args],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Could not find 'pvlist' in PATH. "
            "Load your EPICS environment or add pvAccess/bin/... to PATH."
        ) from exc

def discover_endpoints() -> list[str]:
    """Return unique first tcp@[ ... ] endpoint from each discovered server line."""
    result = run_pvlist([])
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        raise RuntimeError(f"pvlist failed with code {result.returncode}")

    endpoints: list[str] = []
    seen: set[str] = set()
    for line in result.stdout.splitlines():
        match = FIRST_TCP_ENDPOINT_RE.search(line)
        if not match:
            continue
        endpoint = match.group(1)
        if endpoint not in seen:
            seen.add(endpoint)
            endpoints.append(endpoint)
    return endpoints

def main() -> int:
    if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
        print_usage()
        return 0

    try:
        endpoints = discover_endpoints()
        print(f"Discovered {len(endpoints)} PVA servers.", file=sys.stderr)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for endpoint in endpoints:
        result = run_pvlist([endpoint])
        print(f"--- {endpoint} ---", file=sys.stderr)
        if result.stdout:
            sys.stdout.write(result.stdout)
            if not result.stdout.endswith("\n"):
                sys.stdout.write("\n")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
