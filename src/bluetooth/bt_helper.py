from __future__ import absolute_import, print_function, unicode_literals

import os
import dbus

SERVICE_NAME = "org.bluez"
ADAPTER_IFACE = SERVICE_NAME + ".Adapter1"
DEVICE_IFACE = SERVICE_NAME + ".Device1"
OBJ_MGR_IFACE = "org.freedesktop.DBus.ObjectManager"
PROPS_IFACE = "org.freedesktop.DBus.Properties"

STATE_FILE = "mac_address.txt"


def _get_bus():
    return dbus.SystemBus()


def _get_manager():
    bus = _get_bus()
    return dbus.Interface(bus.get_object(SERVICE_NAME, "/"), OBJ_MGR_IFACE)


def get_managed_objects():
    return _get_manager().GetManagedObjects()


def find_adapter(pattern=None):
    bus = _get_bus()
    objects = get_managed_objects()

    for path, ifaces in objects.items():
        adapter = ifaces.get(ADAPTER_IFACE)
        if not adapter:
            continue

        if not pattern or pattern == adapter.get("Address") or path.endswith(pattern):
            obj = bus.get_object(SERVICE_NAME, path)
            return path, dbus.Interface(obj, ADAPTER_IFACE)

    raise RuntimeError("Bluetooth adapter not found")


def find_device(address, adapter_pattern=None):
    bus = _get_bus()
    objects = get_managed_objects()

    prefix = ""
    if adapter_pattern:
        prefix, _ = find_adapter(adapter_pattern)

    for path, ifaces in objects.items():
        dev = ifaces.get(DEVICE_IFACE)
        if not dev:
            continue

        if dev.get("Address") == address and path.startswith(prefix):
            obj = bus.get_object(SERVICE_NAME, path)
            return path, dbus.Interface(obj, DEVICE_IFACE)

    raise RuntimeError("Bluetooth device not found: %s" % address)


def connected_devices():
    objects = get_managed_objects()
    out = []

    for path, ifaces in objects.items():
        dev = ifaces.get(DEVICE_IFACE)
        if dev and dev.get("Connected", False):
            out.append((path, dev))

    return out


def is_connected():
    return bool(connected_devices())


def get_mac_address():
    devs = connected_devices()
    if not devs:
        return None
    current = devs[0][1].get("Address")
    return current

def load_last_mac():
    if not os.path.isfile(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        return f.read().strip() or None


def save_mac(addr):
    if not addr:
        return
    with open(STATE_FILE, "w") as f:
        f.write(addr)

def set_discoverable(onoff):
    path, _ = find_adapter()
    bus = _get_bus()
    props = dbus.Interface(bus.get_object(SERVICE_NAME, path), PROPS_IFACE)
    props.Set(ADAPTER_IFACE, "Discoverable", bool(onoff))


def connect_mac(address, adapter_pattern=None):
    try:
        _, dev = find_device(address, adapter_pattern)
        dev.Connect()
        return True
    except Exception as e:
        print("connect_mac error:", e)
        return False

def clear_paired_devices():
    try:
        managed_objects = get_managed_objects()
        adapter_path, adapter = find_adapter()
        for path, ifaces in managed_objects.items():
            dev = ifaces.get(DEVICE_IFACE)
            if not dev:
                continue
            try:
                adapter.RemoveDevice(path)
                print("Removed device:", dev.get("Address"), "at", path)
            except Exception as e:
                print("Failed to remove device at", path, ":", e)
        if os.path.isfile(STATE_FILE):
            os.remove(STATE_FILE)
    except Exception as e:
        print("unpair_all error:", e)