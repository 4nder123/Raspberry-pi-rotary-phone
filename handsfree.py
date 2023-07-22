from subprocess import Popen, PIPE
import sys
import dbus

class handsfree:
    
    def __init__(self):
        self.aplay_sco = None
        self.aplay_mic = None
        self.arec_mic = None
        self.bluealsa_aplay_exec = "/usr/bin/bluealsa-aplay"
        self.aplay_exec = "/usr/bin/aplay"
        self.arecord_exec = "/usr/bin/arecord"
        self.bus = dbus.SystemBus()
        manager = dbus.Interface(self.bus.get_object('org.ofono', '/'),'org.ofono.Manager')
        self.modems = manager.GetModems()
        
    def anwser_calls(self):
        for path, properties in self.modems:
            print("[ %s ]" % (path))
            if "org.ofono.VoiceCallManager" not in properties["Interfaces"]:
                continue
            mgr = dbus.Interface(self.bus.get_object('org.ofono', path),
                            'org.ofono.VoiceCallManager')
            calls = mgr.GetCalls()

            for path, properties in calls:
                state = properties["State"]
                print("[ %s ] %s" % (path, state))
                if state != "incoming":
                    continue
                call = dbus.Interface(self.bus.get_object('org.ofono', path),
                                'org.ofono.VoiceCall')
                call.Answer()
            
    def hangup(self):
        modem = self.modems[0][0]
        manager = dbus.Interface(self.bus.get_object('org.ofono', modem),
                                'org.ofono.VoiceCallManager')

        manager.HangupAll()
        
    def dial_number(self, number):
        pass

    def list_calls(self):
        pass
    
    def on_call_start(self):
        if self.aplay_sco is None:
            self.aplay_sco = Popen([self.bluealsa_aplay_exec, "--profile-sco"],
                                   stdout=PIPE, stderr=PIPE, shell=False)

        # Terminate aplay and arecord if already running
        if self.aplay_mic is not None:
            self.aplay_mic.terminate()
            self.aplay_mic.wait()

            self.aplay_mic = None
        if self.arec_mic is not None:
            self.arec_mic.terminate()
            self.arec_mic.wait()

            self.arec_mic = None

        device_id = "88:9F:6F:22:BE:55"
        # Pipe Arecord output to Aplay to send over the SCO link
        self.arec_mic = Popen([self.arecord_exec, "-D plughw:1 -f S16_LE -c 1 -r 16000 mic.wav"],
                              stdout=PIPE, shell=False)
        self.aplay_mic = Popen([self.aplay_exec, "-D bluealsa:SRV=org.bluealsa,DEV=88:9F:6F:22:BE:55,PROFILE=sco mic.wav"],
                               stdout=PIPE, stdin=self.arec_mic.stdout, shell=False)
