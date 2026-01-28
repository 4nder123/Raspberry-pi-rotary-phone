import RPi.GPIO as GPIO

class Dial:
    def __init__(self, pulse_pin, switch_pin, tone):
        self.pulse_pin = pulse_pin
        self.switch_pin = switch_pin
        self.tone = tone

        self.pulse_count = 0
        self.collected_digits = ""

        self.is_dialing = False
        self.is_pulse_active = False
        self.is_switch_closed = False

    def start(self):
        self.is_dialing = True
        self.pulse_count = 0
        self.collected_digits = ""
        self.tone.play()

    def stop(self):
        self.is_dialing = False
        self.tone.stop()
        
    def handle_switch_change(self, channel):
        switch_state = GPIO.input(self.switch_pin)

        if switch_state:
            if self.is_dialing and self.pulse_count > 0:
                digit = 0 if self.pulse_count == 10 else self.pulse_count
                self.collected_digits += str(digit)

            self.pulse_count = 0
            self.is_switch_closed = False
        else:
            self.is_switch_closed = True

    def handle_pulse(self, channel):
        pulse_state = GPIO.input(self.pulse_pin)

        if pulse_state and not self.is_pulse_active:
            self.is_pulse_active = True
            self.tone.pause()
            self.pulse_count += 1
        elif not pulse_state and self.is_pulse_active:
            self.is_pulse_active = False
            self.tone.play()

    def get_number(self):
        return self.collected_digits
    
    def is_counting(self):
        return self.is_switch_closed