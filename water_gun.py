#!/usr/bin/env python3
import time
import threading
import RPi.GPIO as GPIO

DEFAULT_PIN = 17
HOLD_TIME = 1  # seconds

class WaterGun:
    def __init__(self, pin=DEFAULT_PIN, default_hold_time=HOLD_TIME):
        self.pin = pin
        self.default_hold_time = default_hold_time

        # Time in the future when the pin should go LOW
        self.next_cutoff_time = 0.0
        
        # A lock to ensure we update/read the cutoff time safely across threads
        self.cutoff_lock = threading.Lock()
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
        
        # Start background monitor thread
        self.monitor_thread = threading.Thread(target=self._pin_monitor, daemon=True)
        self.monitor_thread.start()

    def fire(self):
        print(f"Firing water gun for {HOLD_TIME} seconds...")
        
        with self.cutoff_lock:
            GPIO.output(self.pin, GPIO.HIGH)
            self.next_cutoff_time = time.time() + HOLD_TIME

    def _pin_monitor(self):
        while True:
            time.sleep(0.1)  # short delay so we don't hog CPU
            with self.cutoff_lock:
                if time.time() > self.next_cutoff_time:
                    GPIO.output(self.pin, GPIO.LOW)

