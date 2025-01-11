import time

import Motor

motor = Motor.Motor()

while True:
    try:
        while True:
            motor.move(1)
            time.sleep(3)
            motor.move(0)
            time.sleep(1)
            motor.move(2)
            time.sleep(3)
            motor.move(0)
            time.sleep(1)
    except KeyboardInterrupt:
        motor.cleanup()
