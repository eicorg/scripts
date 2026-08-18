#!/usr/bin/env python3
"""List active EPICS PVAccess PVs by querying discovered PVA servers."""
__version__ = 'v0.0.6 2026-08-18'# added option: -d to print only unique device names
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
        "  pvaccesslist.py -d\n"
        "  pvaccesslist.py\n"
        "  pvaccesslist.py > pvs.txt\n"
        "  python3 -m pvaccesslist.pvaccesslist\n"
        "Options:\n"
        "  -h, --help  Show this help message and exit.\n"
        "  -d          Print only unique device names.\n"
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

def extract_pv_names(text: str) -> list[str]:
    """Extract PV names from `pvlist <ip:port>` output."""
    pvs: list[str] = []
    for line in text.splitlines():
        pvname = line.strip()
        if not pvname:
            continue
        if pvname.startswith(("GUID ", "Error", "error", "WARNING", "warning")):
            continue
        pvs.append(pvname)
    return pvs

def main() -> int:
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print_usage()
        return 0

    allowed = {"-h", "--help", "-d"}
    unknown = [arg for arg in args if arg.startswith("-") and arg not in allowed]
    if unknown:
        print(f"Error: unknown option(s): {' '.join(unknown)}", file=sys.stderr)
        print_usage()
        return 2

    device_only = "-d" in args

    try:
        endpoints = discover_endpoints()
        print(f"Discovered {len(endpoints)} PVA servers.", file=sys.stderr)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    devices_seen: set[str] = set()
    devices: list[str] = []

    for endpoint in endpoints:
        result = run_pvlist([endpoint])
        if device_only:
            for pvname in extract_pv_names(result.stdout):
                device = pvname.split(":")[0]
                if device and device not in devices_seen:
                    devices_seen.add(device)
                    devices.append(device)
        else:
            print(f"--- {endpoint} ---", file=sys.stderr)
            if result.stdout:
                sys.stdout.write(result.stdout)
                if not result.stdout.endswith("\n"):
                    sys.stdout.write("\n")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)

    if device_only:
        for device in devices:
            print(device)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
