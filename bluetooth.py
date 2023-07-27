import dbus

class bluetooth:
    def __init__(self):
        self.bus = dbus.SystemBus()
        
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
                return obj[path].get('org.bluez.Device1', {}).get('Address')
            else:
                wait_until_connected(self)
    
    def enable_discovarable(self):
        manager = dbus.Interface(self.bus.get_object('org.bluez', '/org/bluez/hci0'), "org.freedesktop.DBus.Propeties")
        manager.Set('org.bluez.Adapter1', 'Discoverable', True)
        
    def disable_discovarable(self):
        manager = dbus.Interface(self.bus.get_object('org.bluez', '/org/bluez/hci0'), "org.freedesktop.DBus.Propeties")
        manager.Set('org.bluez.Adapter1', 'Discoverable', False)
        
    def wait_until_connected(self):
        self.enable_discovarable()
        while not self.is_connected():
            pass
        self.disable_discovarable()
        self.get_mac_address()