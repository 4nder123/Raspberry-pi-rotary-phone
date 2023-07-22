from subprocess import Popen, PIPE
from gi.repository import GLib
from time import sleep
import subprocess
import dbus

class audio_route:
    def __init__(self):
        self.aplay_sco = None
        self.aplay_mic = None
        self.arec_mic = None
        self.bluealsa_aplay = "/usr/bin/bluealsa-aplay"
        self.aplay = "/usr/bin/aplay"
        self.arecord = "/usr/bin/arecord"
        self.device_id = "88:9F:6F:22:BE:55"
        
        self.bus = dbus.SystemBus()
        self.bus.add_signal_receiver(
            self._on_bluealsa_pcm_added,
            bus_name='org.bluealsa',
            signal_name='PCMAdded'
        )
        
    def _on_bluealsa_pcm_added(self, path, properties):
        self.set_volumes()

    def set_volumes(self):
        # Set the SCO volumes
        self._set_bluealsa_volume("SCO playback", 6, "100")
        self._set_bluealsa_volume("SCO capture", 8, "100")
        
    def _set_bluealsa_volume(self, type, numid, value):
        if subprocess.run(['amixer', '-D', 'bluealsa', 'cset', 'numid=' + str(numid), value + "%"], capture_output=True).returncode != 0:
            print("Nonzero exit code while setting " + type + " volume")


    def on_call_start(self):
        if self.aplay_sco is None:
            self.aplay_sco = Popen([self.bluealsa_aplay,"--profile-sco"], stdout=PIPE, stderr=PIPE, shell=False)

        # Terminate aplay and arecord if already running
        if self.aplay_mic is not None:
            self.aplay_mic.terminate()
            self.aplay_mic.wait()
            self.aplay_mic = None
            
        if self.arec_mic is not None:
            self.arec_mic.terminate()
            self.arec_mic.wait()
            self.arec_mic = None
    
        # Pipe Arecord output to Aplay to send over the SCO link
        self.arec_mic = Popen([self.arecord,"-D","plughw:1", "-f", "S16_LE", "-c", "1", "-r", "16000", "mic.wav"], stdout=PIPE, shell=False)
        self.aplay_mic = Popen([self.aplay,"-D", "bluealsa:SRV=org.bluealsa,DEV="+self.device_id+",PROFILE=sco", "mic.wav"], stdout=PIPE, stdin=self.arec_mic.stdout, shell=False)
        
     def on_call_stop(self):
        if self.aplay_mic is not None:
            self.aplay_mic.terminate()
            self.aplay_mic.wait()
            self.aplay_mic = None

        if self.arec_mic is not None:
            self.arec_mic.terminate()
            self.arec_mic.kill()
            self.arec_mic = None

        if self.aplay_sco is not None:
            self.aplay_sco.terminate()
            self.aplay_sco.wait()
            self.aplay_sco = None
