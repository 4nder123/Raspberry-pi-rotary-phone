import numpy as np
import sounddevice as sd

class Tone:
    def __init__(self, frequency, samplerate=44100):
        self.samplerate = samplerate
        self.frequency = frequency

    def callback(self, outdata, frames, time, status):
        if self.playing:
            t = (self.start_idx + np.arange(frames)) / self.samplerate
            t = t.reshape(-1, 1)
            outdata[:] = 0.5 * np.sin(2 * np.pi * self.frequency * t)
            self.start_idx += frames
        else:
            outdata.fill(0)

    def play(self):
        self.playing = True
        self.start_idx = 0
        self.stream = sd.OutputStream(samplerate=self.samplerate, channels=1, callback=self.callback)
        self.stream.start()

    def stop(self):
        self.stream.stop()
        self.stream.close()

    def pause(self):
        self.playing = False

    def unpause(self):
        self.playing = True