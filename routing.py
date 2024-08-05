from subprocess import Popen, PIPE
from threading import Thread
from gi.repository import GLib
from time import sleep
import subprocess
import dbus

class audio_route:
    aplay_sco = None
    arec_sco = None
    aplay_mic = None
    arec_mic = None
    def __init__(self):
        self.aplay = "/usr/bin/aplay"
        self.arecord = "/usr/bin/arecord"
        self.device_id = ""
        self.bus = dbus.SystemBus()
        self.bus.add_signal_receiver(
            self._on_bluealsa_pcm_added,
            bus_name='org.bluealsa',
            signal_name='PCMAdded'
        )
        
    def _on_bluealsa_pcm_added(self, path, properties):
        self.set_volumes()

    def set_volumes(self):
        self._set_bluealsa_volume("SCO playback", 6, "100")
        self._set_bluealsa_volume("SCO capture", 8, "100")
        
    def _set_bluealsa_volume(self, type, numid, value):
        if subprocess.run(['amixer', '-D', 'bluealsa', 'cset', 'numid=' + str(numid), value + "%"], capture_output=True).returncode != 0:
            print("Nonzero exit code while setting " + type + " volume")

    def on_call_start(self):
        if self.device_id != "":
            self.clear_sound()
            self.arec_sco = Popen([self.arecord,"-D", "bluealsa:SRV=org.bluealsa,DEV="+self.device_id+",PROFILE=sco", "-t", "raw", "-f", "s16_le", "-c", "1", "-r", "8000","--period-time=20000", "--buffer-time=60000"], stdout=PIPE, stderr=PIPE, shell=False)
            self.aplay_sco = Popen([self.aplay, "-D", "plughw:1,0", "-t", "raw","-f", "s16_le", "-c", "1", "-r", "8000", "--period-time=10000", "--buffer-time=30000"], stdout=PIPE, stdin=self.arec_sco.stdout, stderr=PIPE, shell=False)
            # Pipe Arecord output to Aplay to send over the SCO link
            self.arec_mic = Popen([self.arecord,"-D","plughw:1,0", "-t", "raw", "-f", "s16_le", "-c", "1", "-r", "8000","--period-time=10000", "--buffer-time=30000"], stdout=PIPE, stderr=PIPE, shell=False)
            self.aplay_mic = Popen([self.aplay, "-D", "bluealsa:SRV=org.bluealsa,DEV="+self.device_id+",PROFILE=sco", "-t", "raw","-f", "s16_le", "-c", "1", "-r", "8000", "--period-time=20000", "--buffer-time=60000"], stdout=PIPE, stderr=PIPE, stdin=self.arec_mic.stdout, shell=False)
        
    def clear_sound(self):
        if self.aplay_sco is not None:
            self.aplay_sco.kill()
            self.aplay_sco = None
        if self.arec_sco is not None:
            self.arec_sco.kill()
            self.arec_sco = None
        if self.aplay_mic is not None:
            self.aplay_mic.kill()
            self.aplay_mic = None
        if self.arec_mic is not None:
            self.arec_mic.kill()
            self.arec_mic = None
            
    def close_dial_sound(self):
        self.dial.kill()
        
    def dial_sound(self):
        self.dial = Popen([self.aplay,"-D","plughw:1,0","-f", "s16_le", "-c", "1", "-r", "8000", "--period-time=10000", "--buffer-time=30000","tone.wav"], stdout=PIPE, shell=False)
