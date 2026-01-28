import numpy as np
import sounddevice as sd

class Tone:
    def __init__(self, frequency, samplerate=48000, duration=5):
        self.samplerate = samplerate
        self.frequency = frequency
        self.playing = False
        self.start_idx = 0
        self.stream = None

        t = np.arange(int(self.samplerate * duration)) / self.samplerate
        wave = 0.5 * np.sin(2 * np.pi * self.frequency * t)

        self.waveform = wave.astype(np.float32)
        self.length = len(self.waveform)

    def callback(self, outdata, frames, time, status):
        if status:
            print(status)
        if not self.playing: 
            outdata.fill(0) 
            return
        end = self.start_idx + frames 
        if end < self.length: 
            outdata[:, 0] = self.waveform[self.start_idx:end] 
        else: 
            idx = self.length - self.start_idx 
            outdata[:idx, 0] = self.waveform[self.start_idx:] 
            outdata[idx:, 0] = self.waveform[:frames - idx] 
        self.start_idx = end % self.length

    def play(self):
        if self.playing:
            return
        self.playing = True
        if self.stream is not None:
            return
        self.start_idx = 0
        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=1,
            callback=self.callback,
            blocksize=256,
            latency='low'
        )
        self.stream.start()

    def pause(self):
        self.playing = False

    def stop(self):
        self.playing = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.start_idx = 0
