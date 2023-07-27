import dbus
import os

class bluetooth:
    def __init__(self):
        self.bus = dbus.SystemBus()
        
    def get_managed_objects(self):
        manager = dbus.Interface(self.bus.get_object("org.bluez", "/"),
                    "org.freedesktop.DBus.ObjectManager")
        return manager.GetManagedObjects()

    def find_adapter(self, pattern=None):
        return self.find_adapter_in_objects(self.get_managed_objects(), pattern)

    def find_adapter_in_objects(self, objects, pattern=None):
        for path, ifaces in objects.items():
            adapter = ifaces.get('org.bluez.Adapter1')
            if adapter is None:
                continue
            if not pattern or pattern == adapter:
                obj = self.bus.get_object('org.bluez', path)
                return dbus.Interface(obj, 'org.bluez.Adapter1')
        raise Exception("Bluetooth adapter not found")

    def find_device(self, device_address, adapter_pattern=None):
        return self.find_device_in_objects(self.get_managed_objects(), device_address,
                                    adapter_pattern)

    def find_device_in_objects(self, objects, device_address, adapter_pattern=None):
        path_prefix = ""
        if adapter_pattern:
            adapter = self.find_adapter_in_objects(objects, adapter_pattern)
            path_prefix = adapter.object_path
        for path, ifaces in objects.items():
            device = ifaces.get('org.bluez.Device1')
            if device is None:
                continue
            if (device["Address"] == device_address and
                            path.startswith(path_prefix)):
                obj = self.bus.get_object('org.bluez', path)
                return dbus.Interface(obj, 'org.bluez.Device1')

        raise Exception("Bluetooth device not found")
    
    def is_connected(self):
        manager = dbus.Interface(dbus.Interface(self.bus.get_object('org.bluez', '/'),'org.bluez.Device1'), "org.freedesktop.DBus.ObjectManager")
        obj = manager.GetManagedObjects()
        for path in obj:
            con = obj[path].get('org.bluez.Device1', {}).get('Connected', False)
            if con:
                return True
        return False
        
    def get_mac_address(self):
        manager = dbus.Interface(dbus.Interface(self.bus.get_object('org.bluez', '/'),'org.bluez.Device1'), "org.freedesktop.DBus.ObjectManager")
        obj = manager.GetManagedObjects()
        for path in obj:
            con = obj[path].get('org.bluez.Device1', {}).get('Connected', False)
            if con:
                address = obj[path].get('org.bluez.Device1', {}).get('Address')
                with open("mac_address.txt","a+") as f:
                    f.seek(0)
                    for mac_address in f.read().split(','):
                        if mac_address == address:
                            return address
                    f.write(address+",")
                return address
        return None
    
    def discovarable(self, onoff):
        adapter = dbus.Interface(self.bus.get_object("org.bluez", self.find_adapter().object_path),"org.freedesktop.DBus.Properties")
        adapter.Set("org.bluez.Adapter1", "Discoverable", onoff)
        
    def connect(self):
        with open("mac_address.txt","a+") as f:
            f.seek(0)
            mac_addresses = f.readline().split(",")
            for mac_address in mac_addresses:
                try:
                    if not self.is_connected():
                        device = self.find_device(mac_address)
                        device.Connect()
                except:
                    pass
                
    def unpair_all(self):
        if os.path.isfile("./mac_address.txt"):
            with open("mac_address.txt","a+") as f:
                f.seek(0)
                mac_addresses = f.readline().split(",")
                for mac_address in mac_addresses:
                    managed_objects = self.get_managed_objects()
                    adapter = self.find_adapter_in_objects(managed_objects,)
                    try:
                        dev = self.find_device_in_objects(managed_objects,mac_address)
                        path = dev.object_path
                        adapter.RemoveDevice(path)
                    except:
                        pass
            os.remove("mac_address.txt")
            
    def wait_until_connected(self):
        self.discovarable(True)
        while not self.is_connected():
            print("Trying to connect")
            self.connect()
            sleep(1)
        self.discovarable(False)
        self.get_mac_address()
