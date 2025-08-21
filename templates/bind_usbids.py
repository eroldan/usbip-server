#!/usr/bin/python3

import subprocess
import sys, os
import fnmatch


def load_patterns(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        # Strip whitespace, ignore empty lines and comments
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def parse_devices_from_lines(lines):
    devices = []
    header_end = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('---'):
            header_end = i
            break

    for line in lines[header_end+1:]:
        parts = line.strip().split(None, 6)
        if len(parts) < 5:
            continue  # malformed line
        busid, busdev1, busdev2, vidpid, discard, discard, name = parts
        devices.append({
            'busid': busid,
            'busdev': f"{busdev1} {busdev2}",
            'vidpid': vidpid,
            'name': name
        })
    return devices

def matches(name, patterns):
    name_lower = name.lower()
    for pat in patterns:
        if fnmatch.fnmatch(name_lower, pat.lower()):
            return True
    return False

def main():
    """
    Main entry point for binding USB devices using usbip based on matching rules.
    This function performs the following steps:
    1. Locates the 'usbip' executable in standard system paths.
    2. Parses command-line arguments to obtain the devices file (or stdin) and the rules file.
    3. Loads matching patterns from the specified rules file.
    4. Reads the list of USB devices from the provided file or standard input.
    5. Parses device information from the input lines.
    6. For each device, checks if its name matches any of the loaded patterns.
    7. If a match is found, constructs and runs the 'usbip bind' command for the device.
    """

    usbip_path = None
    for path in ['/usr/sbin/usbip', '/usr/bin/usbip']:
        if os.path.isfile(path):
            usbip_path = path
            break
    else:
        print("[ERROR] usbip not found in /usr/sbin or /usr/bin")
        sys.exit(1)

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} devices_file.txt|'-' rulesfile.txt")
        sys.exit(1)

    devices_source = sys.argv[1]
    patterns_file = sys.argv[2]

    # Load patterns
    patterns = load_patterns(patterns_file)

    # Read devices lines
    if devices_source == '-':
        lines = sys.stdin.read().splitlines()
    else:
        with open(devices_source, 'r', encoding='utf-8') as f:
            lines = f.readlines()

    devices = parse_devices_from_lines(lines)

    for dev in devices:
        if matches(dev['name'], patterns):
            cmd = [usbip_path, 'bind', '--busid', dev['busid']]
            print(f"Binding device: {dev['busid']} ({dev['name']})")
            print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=False)

if __name__ == '__main__':
    main()
