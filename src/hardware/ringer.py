from threading import Thread
from gpiozero import Motor
from time import sleep, time

class Ringer:
    def __init__(self, ringer_pins, ring_on_seconds, ring_off_seconds):
        self.forward_pin, self.backward_pin = ringer_pins
        self.ringer = Motor(forward=self.forward_pin, backward=self.backward_pin)
        self.ring_on_seconds = ring_on_seconds
        self.ring_off_seconds = ring_off_seconds
        self.isRinging = False
        self.ring_thread = None

    def _ring_loop(self, strike_time=0.025):
        self.ringer.forward()
        while self.isRinging:
            t_end = time() + self.ring_on_seconds
            while self.isRinging and time() < t_end:
                self.ringer.reverse()
                sleep(strike_time)
            if not self.isRinging:
                break
            sleep(self.ring_off_seconds)

    def ring(self):
        if self.isRinging:
            return
        self.isRinging = True
        self.ring_thread = Thread(target=self._ring_loop)
        self.ring_thread.start()

    def stop(self):
        self.isRinging = False
        self.ringer.stop()
        if self.ring_thread:
            self.ring_thread.join(timeout=1)
            self.ring_thread = None