import time

import Motor

motor = Motor.Motor()

while True:
    motor.move_forward()
    time.sleep(1)
    motor.stop_moving()
    time.sleep(1)
    motor.move_backward()
    time.sleep(1)
    motor.stop_moving()
    time.sleep(1)
