import RPi.GPIO as GPIO


class Motor:
    def __init__(self):
        self.name = "Motor"
        self.status = 0  # 0: stopped, 1: forward, 2: backward
        self.speed = 50  # 0-100

        # GPIO pins
        self.in1 = 17
        self.in2 = 27
        self.en_a = 4

        self.in3 = 22
        self.in4 = 23
        self.en_b = 18

        # Set GPIO mode
        GPIO.setmode(GPIO.BCM)

        # Set GPIO pins
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.in3, GPIO.OUT)
        GPIO.setup(self.in4, GPIO.OUT)
        GPIO.setup(self.en_a, GPIO.OUT)
        GPIO.setup(self.en_b, GPIO.OUT)

        # Set PWM
        power1 = GPIO.PWM(self.en_a, 100)
        power2 = GPIO.PWM(self.en_b, 100)
        power1.start(self.speed)
        power2.start(self.speed)

        # Stop the motor at the beginning
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.LOW)

    def move_forward(self):
        print(f"{self.name} is moving forward")
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.HIGH)
        GPIO.output(self.in4, GPIO.LOW)
        self.status = 1

    def stop_moving(self):
        print(f"{self.name} is stopping")
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.LOW)
        self.status = 0

    def move_backward(self):
        print(f"{self.name} is moving backward")
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.HIGH)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.HIGH)
        self.status = 2

    def move(self, direction):
        if direction == 1:
            self.move_forward()
        elif direction == 2:
            self.move_backward()
        else:
            self.stop_moving()
