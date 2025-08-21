#!/usr/bin/python3

import pyudev
import subprocess


def get_lsusb_names():
    """Parse lsusb output into a dict keyed by (busnum, devnum)."""
    lsusb_lines = subprocess.check_output(['/usr/bin/lsusb'], text=True).splitlines()
    names = {}
    for line in lsusb_lines:
        # Format: Bus 001 Device 003: ID 36b0:3035 RDMCTMZT CIDOO QK61
        parts = line.split()
        bus = parts[1]
        dev = parts[3].rstrip(':')
        id_vendor_product = parts[5]
        name = " ".join(parts[6:]) if len(parts) > 6 else ""
        names[(int(bus), int(dev))] = {
            "id": id_vendor_product,
            "name": name,
            "raw_line": line
        }
    return names


def main():
    """
    Lists all connected USB devices with detailed information.

    This function retrieves USB device information using the pyudev library and
    displays a formatted table with the following columns:
        - BusID (sysfs): The sysfs name of the USB device (e.g., "1-1.2").
        - Bus/Device: The bus and device numbers as reported by the system.
        - VID:PID: The vendor and product IDs of the device.
        - Name: The human-readable name of the device, if available.

    The function relies on a helper function `get_lsusb_names()` to map bus and device
    numbers to device names, and prints the information for each detected USB device.
    """
    context = pyudev.Context()
    lsusb_names = get_lsusb_names()

    print(f"{'BusID (sysfs)':<10} {'Bus/Device':<15} {'VID:PID':<15} {'Name'}")
    print("-" * 70)

    for device in context.list_devices(subsystem='usb', DEVTYPE='usb_device'):
        busnum = device.attributes.asint('busnum')
        devnum = device.attributes.asint('devnum')
        sys_name = device.sys_name  # e.g. "1-1.2"

        key = (busnum, devnum)
        lsusb_info = lsusb_names.get(key, {})

        vendor_id = device.attributes.get('idVendor').decode()
        product_id = device.attributes.get('idProduct').decode()
        name = lsusb_info.get('name', '')

        print(f"{sys_name:<10} Bus {busnum:03d} Device {devnum:03d}  {vendor_id}:{product_id}   {name}")


if __name__ == "__main__":
    main()
