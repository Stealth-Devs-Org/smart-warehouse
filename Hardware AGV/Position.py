import RPi.GPIO as GPIO


class Position:
    def __init__(self):
        self.count = 0
        self.total_count = 94
        self.starting_location = [36, 13]
        self.current_location = self.starting_location

        # IR sensor pin
        self.IR_pin = 3

        # Set GPIO mode
        GPIO.setmode(GPIO.BOARD)

        # Set GPIO pin
        GPIO.setup(self.IR_pin, GPIO.IN)

        self.IR_output = GPIO.input(self.IR_pin)

    def detect_IR_output_change(self):
        new_output = GPIO.input(self.IR_pin)
        if new_output != self.IR_output:
            self.IR_output = new_output
            return True
        return False

    def count_position(self, status):
        # if self.detect_IR_output_change():
        if status == 1:
            self.count += 1
        elif status == 2:
            self.count -= 1
        else:
            return None
        self.convert_to_location(self.count)
        print(f"Current location: {self.current_location}")
        print(f"Count: {self.count}")
        return None

    def convert_to_location(self):
        count = self.count
        if count < 3:
            self.current_location = [36, 13 + count]
        elif count < 15:
            self.current_location = [36 - (count - 2), 15]
        elif count < 19:
            self.current_location = [24, 15 + (count - 14)]
        elif count < 32:
            self.current_location = [24 + (count - 18), 19]
        elif count < 35:
            self.current_location = [37, 19 + (count - 31)]
        elif count < 49:
            self.current_location = [37 - (count - 34), 22]
        elif count < 58:
            self.current_location = [23, 22 - (count - 48)]
        elif count < 61:
            self.current_location = [23 - (count - 57), 13]
        elif count < 70:
            self.current_location = [20, 13 - (count - 60)]
        elif count < 80:
            self.current_location = [20 + (count - 69), 4]
        elif count < 88:
            self.current_location = [30, 4 + (count - 79)]
        else:
            self.current_location = [30 + (count - 87), 12]
        return None

    def decide_forward_backward(self, direction):
        count = self.count
        if count < 3:
            if count == 2:
                if direction in ["N", "W"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "N":
                    return 1
                elif direction == "S":
                    return 2

        elif count < 15:
            if count == 14:
                if direction in ["N", "W"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "W":
                    return 1
                elif direction == "E":
                    return 2

        elif count < 19:
            if count == 18:
                if direction in ["N", "E"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "N":
                    return 1
                elif direction == "S":
                    return 2

        elif count < 32:
            if count == 31:
                if direction in ["N", "E"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "E":
                    return 1
                elif direction == "W":
                    return 2

        elif count < 35:
            if count == 34:
                if direction in ["N", "W"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "N":
                    return 1
                elif direction == "S":
                    return 2

        elif count < 49:
            if count == 48:
                if direction in ["S", "W"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "W":
                    return 1
                elif direction == "E":
                    return 2

        elif count < 58:
            if count == 57:
                if direction in ["S", "W"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "S":
                    return 1
                elif direction == "N":
                    return 2

        elif count < 61:
            if count == 60:
                if direction in ["S", "W"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "W":
                    return 1
                elif direction == "E":
                    return 2

        elif count < 70:
            if count == 69:
                if direction in ["S", "E"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "S":
                    return 1
                elif direction == "N":
                    return 2

        elif count < 80:
            if count == 79:
                if direction in ["N", "E"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "E":
                    return 1
                elif direction == "W":
                    return 2

        elif count < 88:
            if count == 87:
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
            if count == 93:
                if direction in ["N", "E"]:
                    return 1
                else:
                    return 2
            else:
                if direction == "E":
                    return 1
                elif direction == "W":
                    return 2
