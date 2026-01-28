#!/usr/bin/env python3
from __future__ import absolute_import, print_function, unicode_literals

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

BUS_NAME = "org.bluez"
AGENT_INTERFACE = "org.bluez.Agent1"
AGENT_PATH = "/org/bluez/agent"


def set_trusted(bus, device_path):
    props = dbus.Interface(
        bus.get_object("org.bluez", device_path),
        "org.freedesktop.DBus.Properties"
    )
    props.Set("org.bluez.Device1", "Trusted", True)


class Agent(dbus.service.Object):
    def __init__(self, bus, path, mainloop):
        super().__init__(bus, path)
        self.mainloop = mainloop
        self.bus = bus

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        print("Agent released")
        self.mainloop.quit()

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        print(f"AuthorizeService: {device} {uuid}")
        set_trusted(self.bus, device)
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print(f"RequestAuthorization: {device}")
        set_trusted(self.bus, device)
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")


if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    mainloop = GLib.MainLoop()
    agent = Agent(bus, AGENT_PATH, mainloop)

    manager = dbus.Interface(
        bus.get_object(BUS_NAME, "/org/bluez"),
        "org.bluez.AgentManager1"
    )

    capability = "NoInputNoOutput"

    print("Registering agent...")
    manager.RegisterAgent(AGENT_PATH, capability)

    print("Requesting default agent...")
    manager.RequestDefaultAgent(AGENT_PATH)

    print("Agent running with NoInputNoOutput")
    mainloop.run()
