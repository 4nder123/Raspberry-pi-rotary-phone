from subprocess import Popen, PIPE
import subprocess
import dbus


class AudioRoute:
    def __init__(self):
        self.aplay = "/usr/bin/aplay"
        self.arecord = "/usr/bin/arecord"
        self.device_id = ""

        self.aplay_sco = None
        self.arec_sco = None
        self.aplay_mic = None
        self.arec_mic = None

        self.bus = dbus.SystemBus()
        self.bus.add_signal_receiver(
            self._on_bluealsa_pcm_added,
            bus_name="org.bluealsa",
            signal_name="PCMAdded"
        )
    
    def handle_bt_connected(self, mac): 
        self.device_id = mac 

    def handle_bt_disconnected(self):
        self.device_id = ""
        self.clear_sound()

    def _on_bluealsa_pcm_added(self, path, properties):
        self.set_volumes()

    def set_volumes(self):
        self._set_bluealsa_volume(6, "100")
        self._set_bluealsa_volume(8, "100")

    def _set_bluealsa_volume(self, numid, value):
        subprocess.run(
            ["amixer", "-D", "bluealsa", "cset", f"numid={numid}", f"{value}%"],
            capture_output=True
        )

    def on_call_start(self):
        if not self.device_id:
            print("No device ID, cannot start audio routing")
            return

        self.clear_sound()

        self.arec_sco = Popen([
            self.arecord,
            "-D", f"bluealsa:SRV=org.bluealsa,DEV={self.device_id},PROFILE=sco",
            "-t", "raw", "-f", "s16_le", "-c", "1", "-r", "8000",
            "--period-time=20000", "--buffer-time=60000"
        ], stdout=PIPE, stderr=PIPE)

        self.aplay_sco = Popen([
            self.aplay,
            "-D", "plughw:1,0",
            "-t", "raw", "-f", "s16_le", "-c", "1", "-r", "8000",
            "--period-time=10000", "--buffer-time=30000"
        ], stdin=self.arec_sco.stdout, stdout=PIPE, stderr=PIPE)

        self.arec_mic = Popen([
            self.arecord,
            "-D", "plughw:1,0",
            "-t", "raw", "-f", "s16_le", "-c", "1", "-r", "8000",
            "--period-time=10000", "--buffer-time=30000"
        ], stdout=PIPE, stderr=PIPE)

        self.aplay_mic = Popen([
            self.aplay,
            "-D", f"bluealsa:SRV=org.bluealsa,DEV={self.device_id},PROFILE=sco",
            "-t", "raw", "-f", "s16_le", "-c", "1", "-r", "8000",
            "--period-time=20000", "--buffer-time=60000"
        ], stdin=self.arec_mic.stdout, stdout=PIPE, stderr=PIPE)

    def _kill(self, proc):
        if proc is not None:
            try:
                proc.kill()
            except:
                pass

    def clear_sound(self):
        self._kill(self.aplay_sco)
        self._kill(self.arec_sco)
        self._kill(self.aplay_mic)
        self._kill(self.arec_mic)

        self.aplay_sco = None
        self.arec_sco = None
        self.aplay_mic = None
        self.arec_mic = None
