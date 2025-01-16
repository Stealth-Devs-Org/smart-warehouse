import threading
import time

import RPi.GPIO as GPIO


class Position:
    def __init__(self):
        self.count = 0
        self.total_count = 58
        self.starting_location = [37, 13]
        self.current_location = self.starting_location

        # IR sensor pin
        self.IR_pin = 4

        # Set GPIO mode
        GPIO.setmode(GPIO.BCM)

        # Set GPIO pin
        GPIO.setup(self.IR_pin, GPIO.IN)

        self.IR_output = GPIO.input(self.IR_pin)

        # threading.Thread(target=self.update_IR_output).start()

    def detect_IR_W2B_change(self):
        time.sleep(0.025)
        new_output = GPIO.input(self.IR_pin)
        old_output = self.IR_output
        self.IR_output = new_output
        if new_output == 1 and old_output == 0:
            print(f"New location reached. IR output: {self.IR_output}")
            return True
        return False

    def detect_IR(self):
        time.sleep(0.025)
        self.IR_output = GPIO.input(self.IR_pin)
        return self.IR_output

    def count_position(self, status):
        # if self.detect_IR_output_change():
        if status == 1:
            self.count += 1
            if self.count == self.total_count:
                self.count = 0
        elif status == 2:
            self.count -= 1
            if self.count == -1:
                self.count = self.total_count - 1
        else:
            return None
        self.convert_to_location()
        print(f"Current location: {self.current_location}")
        print(f"Count: {self.count}")
        return None

    def convert_to_location(self):
        count = self.count
        if count < 7:
            self.current_location = [37, 13 + count]
        elif count < 21:
            self.current_location = [37 - (count - 6), 19]
        elif count < 36:
            self.current_location = [23, 19 - (count - 20)]
        elif count < 43:
            self.current_location = [23 + (count - 35), 4]
        elif count < 51:
            self.current_location = [30, 4 + (count - 42)]
        elif count < 58:
            self.current_location = [30 + (count - 50), 12]

    def decide_forward_backward(self, direction):
        count = self.count
        if count < 7:
            if count == 6:
                if direction in ["N", "W"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "N":
                    return 1
                elif direction == "S":
                    return 2

        elif count < 21:
            if count == 20:
                if direction in ["S", "W"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "W":
                    return 1
                elif direction == "E":
                    return 2

        elif count < 36:
            if count == 35:
                if direction in ["S", "E"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "S":
                    return 1
                elif direction == "N":
                    return 2

        elif count < 43:
            if count == 42:
                if direction in ["N", "E"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "E":
                    return 1
                elif direction == "W":
                    return 2

        elif count < 51:
            if count == 50:
                if direction in ["N", "E"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "N":
                    return 1
                elif direction == "S":
                    return 2

        else:
            if count == 57:
                if direction in ["N", "E"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "E":
                    return 1
                elif direction == "W":
                    return 2

    def update_IR_output(self):
        while True:
            self.IR_output = GPIO.input(self.IR_pin)
            time.sleep(0.05)
