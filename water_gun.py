#!/usr/bin/env python3
import time
import threading
import RPi.GPIO as GPIO

DEFAULT_PIN = 17
DEFAULT_HOLD_TIME = 0.5  # seconds
SERVER_PORT = 8080

class WaterGun:
    def __init__(self, pin=DEFAULT_PIN, default_hold_time=DEFAULT_HOLD_TIME):
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

    def fire(self, hold_time=None):
        """
        Drive the GPIO pin HIGH. Reset the countdown so that
        the pin will go LOW after hold_time seconds from now.
        """
        print(f"Firing water gun for {hold_time or self.default_hold_time} seconds...")
        if hold_time is None:
            hold_time = self.default_hold_time
        
        with self.cutoff_lock:
            GPIO.output(self.pin, GPIO.HIGH)
            self.next_cutoff_time = time.time() + hold_time

    def _pin_monitor(self):
        """
        Background thread function. Loops and checks if the
        current time has passed 'next_cutoff_time'; if so,
        it sets the GPIO pin LOW.
        """
        while True:
            time.sleep(0.05)  # short delay so we don't hog CPU
            with self.cutoff_lock:
                if time.time() > self.next_cutoff_time:
                    GPIO.output(self.pin, GPIO.LOW)

