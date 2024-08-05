from subprocess import call
import dbus
import os

SERVICE_NAME = "org.bluez"
ADAPTER_INTERFACE = SERVICE_NAME + ".Adapter1"
DEVICE_INTERFACE = SERVICE_NAME + ".Device1"

def get_managed_objects():
	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object("org.bluez", "/"),
				"org.freedesktop.DBus.ObjectManager")
	return manager.GetManagedObjects()

def find_adapter(pattern=None):
	return find_adapter_in_objects(get_managed_objects(), pattern)

def find_adapter_in_objects(objects, pattern=None):
	bus = dbus.SystemBus()
	for path, ifaces in objects.items():
		adapter = ifaces.get(ADAPTER_INTERFACE)
		if adapter is None:
			continue
		if not pattern or pattern == adapter["Address"] or \
							path.endswith(pattern):
			obj = bus.get_object(SERVICE_NAME, path)
			return dbus.Interface(obj, ADAPTER_INTERFACE)
	raise Exception("Bluetooth adapter not found")

def find_device(device_address, adapter_pattern=None):
	return find_device_in_objects(get_managed_objects(), device_address,
								adapter_pattern)

def find_device_in_objects(objects, device_address, adapter_pattern=None):
	bus = dbus.SystemBus()
	path_prefix = ""
	if adapter_pattern:
		adapter = find_adapter_in_objects(objects, adapter_pattern)
		path_prefix = adapter.object_path
	for path, ifaces in objects.items():
		device = ifaces.get(DEVICE_INTERFACE)
		if device is None:
			continue
		if (device["Address"] == device_address and
						path.startswith(path_prefix)):
			obj = bus.get_object(SERVICE_NAME, path)
			return dbus.Interface(obj, DEVICE_INTERFACE)

	raise Exception("Bluetooth device not found")

def is_connected():
        bus = dbus.SystemBus()
        manager = dbus.Interface(dbus.Interface(bus.get_object('org.bluez', '/'),'org.bluez.Device1'), "org.freedesktop.DBus.ObjectManager")
        obj = manager.GetManagedObjects()
        for path in obj:
            con = obj[path].get('org.bluez.Device1', {}).get('Connected', False)
            if con:
                return True
        return False
        
def get_mac_address():
    bus = dbus.SystemBus()
    manager = dbus.Interface(dbus.Interface(bus.get_object('org.bluez', '/'),'org.bluez.Device1'), "org.freedesktop.DBus.ObjectManager")
    obj = manager.GetManagedObjects()
    for path in obj:
        con = obj[path].get('org.bluez.Device1', {}).get('Connected', False)
        if con:
            address = obj[path].get('org.bluez.Device1', {}).get('Address')
            if os.path.isfile("./mac_address.txt"):
                with open("mac_address.txt","r") as fr:
                    if fr.readline() == address:
                        return address
            with open("mac_address.txt","w") as fw:
                fw.write(address)
            return address
    return None

def discovarable(onoff):
    bus = dbus.SystemBus()
    adapter = dbus.Interface(bus.get_object("org.bluez", find_adapter().object_path),"org.freedesktop.DBus.Properties")
    adapter.Set("org.bluez.Adapter1", "Discoverable", onoff)
    
def try_autoconnect():
    if os.path.isfile("./mac_address.txt"):
        with open("mac_address.txt","r") as f:
            mac_address = f.readline()
            try:
                if not is_connected():
                    call(["sudo", "/bin/python", "./BluetoothController/agent.py",mac_address])
            except:
                pass
            
def unpair_all():
    if os.path.isfile("./mac_address.txt"):
        managed_objects = get_managed_objects()
        adapter = find_adapter_in_objects(managed_objects,)
        for path, ifaces in managed_objects.items():
            device = ifaces.get(DEVICE_INTERFACE)
            if device is None:
                continue
            try:
                dev = find_device_in_objects(managed_objects, device["Address"])
                path = dev.object_path
                adapter.RemoveDevice(path)
            except:
                pass
        os.remove("mac_address.txt")