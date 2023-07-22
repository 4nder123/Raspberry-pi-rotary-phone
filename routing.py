from subprocess import Popen, PIPE

class audio_route:
    def __init__(self):
        self.aplay_sco = None
        self.aplay_mic = None
        self.arec_mic = None
        self.device_id = "88:9F:6F:22:BE:55"
    
    def on_call_start(self):
        if self.aplay_sco is None:
            self.aplay_sco = Popen(["bluealsa-aplay --profile-sco"], stdout=PIPE, stderr=PIPE, shell=False)

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
        self.arec_mic = Popen(["arecord -D plughw:1 -f S16_LE -c 1 -r 16000 mic.wav"], stdout=PIPE, shell=False)
        self.aplay_mic = Popen(["aplay -D bluealsa:SRV=org.bluealsa,DEV=88:9F:6F:22:BE:55,PROFILE=sco mic.wav"], stdout=PIPE, stdin=self.arec_mic.stdout, shell=False)