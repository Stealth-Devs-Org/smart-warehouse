import threading
import time

import RPi.GPIO as GPIO


class Motor:
    def __init__(self):
        self.name = "Motor"
        self.status = 0  # 0: stopped, 1: forward, 2: backward
        self.speed1 = 100  # 0-100
        self.speed2 = 100  # 0-100

        # Time for moving and stopping in the movement_thread
        self.move_time = 0.03
        self.stop_time = 0.2
        self.movement_thread_started = False

        # GPIO pins
        self.in1 = 27  # 13
        self.in2 = 22  # 15
        self.en_a = 17  # 11

        self.in3 = 23  # 16
        self.in4 = 24  # 18
        self.en_b = 25  # 22

        # Set GPIO mode
        GPIO.setmode(GPIO.BCM)

        # Clear GPIO channels
        GPIO.cleanup()

        # Set GPIO pins
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.in3, GPIO.OUT)
        GPIO.setup(self.in4, GPIO.OUT)
        GPIO.setup(self.en_a, GPIO.OUT)
        GPIO.setup(self.en_b, GPIO.OUT)

        # Set PWM
        self.power1 = GPIO.PWM(self.en_a, 1000)
        self.power2 = GPIO.PWM(self.en_b, 1000)
        self.power1.start(self.speed1)
        self.power2.start(self.speed2)

        # Stop the motor at the beginning
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.LOW)

    def move_forward(self):
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.HIGH)
        GPIO.output(self.in4, GPIO.LOW)

    def stop_moving(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.LOW)

        # GPIO.output(self.in1, GPIO.HIGH)
        # GPIO.output(self.in2, GPIO.HIGH)
        # GPIO.output(self.in3, GPIO.HIGH)
        # GPIO.output(self.in4, GPIO.HIGH)

    def move_backward(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.HIGH)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.HIGH)

    def move(self, direction):
        if direction == 1:
            self.status = 1
            if not hasattr(self, "movement_thread_started") or not self.movement_thread_started:
                self.movement_thread_started = True
                threading.Thread(target=self.movement_thread).start()

        elif direction == 2:
            self.status = 2
            # print(f"{self.name} is moving backward")
            if not hasattr(self, "movement_thread_started") or not self.movement_thread_started:
                self.movement_thread_started = True
                threading.Thread(target=self.movement_thread).start()
        else:
            self.status = 0
            # print(f"{self.name} is stopping")
            self.stop_moving()

    def movement_thread(self):
        if self.status == 1:
            print(f"{self.name} is moving forward")
        elif self.status == 2:
            print(f"{self.name} is moving backward")
        else:
            print(f"{self.name} is stopping")
        while self.status != 0:
            if self.status == 1:
                self.move_forward()
            elif self.status == 2:
                self.move_backward()
            time.sleep(self.move_time)
            self.stop_moving()
            time.sleep(self.stop_time)
        self.movement_thread_started = False

    def cleanup(self):
        self.status = 0
        self.movement_thread_started = False
        self.stop_moving()
        GPIO.cleanup()
