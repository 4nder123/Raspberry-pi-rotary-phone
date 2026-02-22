import RPi.GPIO as GPIO
from time import sleep, time
from gi.repository import GLib
from src.hardware.ringer import Ringer
from src.hardware.dial import Dial
from src.audio.tone import Tone
from src.audio.routing import AudioRoute
from src.bluetooth.bluetooth import Bluetooth
from src.bluetooth.handsfree import HandsFree
from config import (
    HOOK_PIN,
    DIAL_PULSE_PIN, 
    DIAL_SWITCH_PIN, 
    DIAL_COLLECT_TIMEOUT_SECONDS,
    IDLE_SLEEP_SECONDS,
    BT_CHECK_INTERVAL,
    RING_OFF_SECONDS, 
    RING_ON_SECONDS, 
    RINGER_PINS,
    DIAL_TONE_FREQUENCY_HZ,
)

class RotaryPhone:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(HOOK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(DIAL_PULSE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(DIAL_SWITCH_PIN , GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.ringer = Ringer(RINGER_PINS, RING_ON_SECONDS, RING_OFF_SECONDS)
        self.tone = Tone(DIAL_TONE_FREQUENCY_HZ)
        self.dial = Dial(DIAL_PULSE_PIN, DIAL_SWITCH_PIN, self.tone)
        self.hf = HandsFree()
        self.route = AudioRoute()
        self.bt = Bluetooth(
            on_connected=self.on_bt_connected,
            on_disconnected=self.on_bt_disconnected,
            reconnect_interval=BT_CHECK_INTERVAL
        )
        self.is_call = False
        self.is_phone_up = GPIO.input(HOOK_PIN) 

    def on_bt_connected(self, mac):
        print("Bluetooth connected:", mac)
        self.route.handle_bt_connected(mac)
        self.hf.bt_connected()

    def on_bt_disconnected(self):
        print("Bluetooth disconnected")
        self.route.handle_bt_disconnected()
        self.hf.bt_disconnected()

    def ring(self):
        if self.hf.get_calls_state() != "incoming" or not GPIO.input(HOOK_PIN):
            self.ringer.stop()
            return False
        GLib.timeout_add(50, self.ring)
        return False

    def call_number(self):
        self.dial.start()
        self.dial_timeout = time() + DIAL_COLLECT_TIMEOUT_SECONDS
        GLib.timeout_add(500, self._check_dial)

    def _check_dial(self):
        if GPIO.input(HOOK_PIN):
            self.dial.stop()
            return False
        
        if time() >= self.dial_timeout:
            self.dial.stop()
            nr = self.dial.get_number()
            if nr == "0000":
                self.bt.clear_paired_devices()
            elif nr == "1111":
                self.bt.set_discoverable(True)
            elif nr:
                self.hf.dial_number(nr)
                self.is_call = True
                self.start_call()
            return False
        
        if self.hf.get_calls_state() in ("active", "dialing"):
            self.dial.stop()
            self.is_call = True
            self.start_call()
            return False
        
        if self.dial.get_number() == "" or self.dial.is_counting():
            self.dial_timeout = time() + DIAL_COLLECT_TIMEOUT_SECONDS
        
        GLib.timeout_add(50, self._check_dial)
        return False

    def idle(self):
        if not GPIO.input(HOOK_PIN):
            return False
        
        if self.is_call:
            self.route.clear_sound()
            self.hf.hangup()
            self.is_call = False

        if self.hf.get_calls_state() == "incoming":
            self.ringer.ring()
            self.ring()
        
        GLib.timeout_add(int(IDLE_SLEEP_SECONDS * 1000), self.idle)
        return False 

    def phone_up(self):
        state = self.hf.get_calls_state()

        if state == "incoming":
            self.is_call = True
            self.hf.answer_calls()
            self.start_call()
            return

        if state in ("active", "dialing"):
            self.is_call = True
            self.start_call()
            return
        
        self.tone.play()
        self.call_number()

    def hook_event(self, channel):
        off_hook = (not GPIO.input(HOOK_PIN))

        if off_hook and not self.is_phone_up:
            self.is_phone_up = True
            self.phone_up()
        elif (not off_hook) and self.is_phone_up:
            self.is_phone_up = False
            self.idle()

    def start_call(self):
        self.tone.stop()
        self.route.on_call_start()

    def start(self):
        GPIO.add_event_detect(HOOK_PIN, GPIO.BOTH, callback=self.hook_event)
        GPIO.add_event_detect(DIAL_PULSE_PIN, GPIO.BOTH, callback=self.dial.handle_pulse)
        GPIO.add_event_detect(DIAL_SWITCH_PIN, GPIO.BOTH, callback=self.dial.handle_switch_change)
        self.hook_event(0)

    def cleanup(self):
        try:
            self.ringer.stop()
        except Exception:
            pass

        try:
            self.tone.stop()
        except Exception:
            pass

        try:
            self.route.clear_sound()
        except Exception:
            pass

    
    