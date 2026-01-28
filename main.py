import atexit

import RPi.GPIO as GPIO
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from src.phone.rotaryphone import RotaryPhone


def _cleanup_all(phone):
    try:
        phone.cleanup()
    except Exception:
        pass
    try:
        GPIO.cleanup()
    except Exception:
        pass

def start():
    phone = RotaryPhone()
    atexit.register(_cleanup_all, phone)
    phone.start()
    return False  # Run only once

def main():
    DBusGMainLoop(set_as_default=True)
    loop = GLib.MainLoop()
    GLib.idle_add(start)
    loop.run()


if __name__ == "__main__":
    main()
    

