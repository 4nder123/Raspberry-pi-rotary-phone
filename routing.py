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
        self.bluealsa_aplay = "/usr/bin/bluealsa-aplay"
        self.aplay = "/usr/bin/aplay"
        self.arecord = "/usr/bin/arecord"
        self.device_id = "88:9F:6F:22:BE:55"
        
        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(self.bus.get_object('org.ofono', '/'), 'org.ofono.Manager')
        self.bus.add_signal_receiver(
            self._on_bluealsa_pcm_added,
            bus_name='org.bluealsa',
            signal_name='PCMAdded'
        )
        
    def run(self):
        thread = Thread(target=self.poll, daemon=True)
        thread.start()
        
    def poll(self):
        audio_routing_begun = False
        while True:
            modems = self.manager.GetModems()  # Update list in case of new modems from newly-paired devices
            for modem, modem_props in modems:
                if "org.ofono.VoiceCallManager" not in modem_props["Interfaces"]:
                    continue
                mgr = dbus.Interface(self.bus.get_object('org.ofono', modem), 'org.ofono.VoiceCallManager')
                calls = mgr.GetCalls()
                # Due to polling we aren't able to catch when calls end up disconnecting, so we just overwrite the list
                # each time.
                currentcalls = {}
                for path, properties in calls:
                    state = properties['State']
                    name = properties['Name']
                    line_ident = properties['LineIdentification']

                    if state != "disconnected":
                        currentcalls[line_ident] = {
                            "path": path,
                            "state": state,
                            "name": name,
                            "modem": modem
                        }

                calls = currentcalls
                if len(calls) > 0 and audio_routing_begun == False:
                    audio_routing_begun = True
                    self.on_call_start()
                elif len(calls) == 0 and audio_routing_begun != False:
                    audio_routing_begun = False
                    self.on_call_end()
            sleep(1)
    
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
        
        self.arec_sco = Popen([self.arecord,"-D", "bluealsa:SRV=org.bluealsa,DEV="+self.device_id+",PROFILE=sco", "-t", "raw", "-f", "s16_le", "-c", "1", "-r", "8000","--period-time=20000", "--buffer-time=60000"], stdout=PIPE, stderr=PIPE, shell=False)
        self.aplay_sco = Popen([self.aplay, "-D", "plughw:1,0", "-t", "raw","-f", "s16_le", "-c", "1", "-r", "8000", "--period-time=10000", "--buffer-time=30000"], stdout=PIPE, stdin=self.arec_sco.stdout, stderr=PIPE, shell=False)

        # Pipe Arecord output to Aplay to send over the SCO link
        self.arec_mic = Popen([self.arecord,"-D","plughw:1,0", "-t", "raw", "-f", "s16_le", "-c", "1", "-r", "8000","--period-time=10000", "--buffer-time=30000"], stdout=PIPE, shell=False)
        self.aplay_mic = Popen([self.aplay, "-D", "bluealsa:SRV=org.bluealsa,DEV="+self.device_id+",PROFILE=sco", "-t", "raw","-f", "s16_le", "-c", "1", "-r", "8000", "--period-time=20000", "--buffer-time=60000"], stdout=PIPE, stdin=self.arec_mic.stdout, shell=False)
        
    def on_call_end(self):
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
            
    def dial_sound(self, stop_sound):
        dial = Popen([self.aplay,"-D","plughw:1,0","-f", "s16_le", "-c", "1", "-r", "8000", "--period-time=10000", "--buffer-time=30000","tone.wav"], stdout=PIPE, shell=False)
        while True:
            if stop_sound:
                dial.kill()
                break
