import threading
import time

import Motor
import Position

motor = Motor.Motor()
position = Position.Position()

for_or_back = 1


def UpdateCurrentLocation():
    prev_for_or_back = 0
    skip_count = False

    while True:
        while not position.detect_IR_W2B_change():
            time.sleep(0)

        if prev_for_or_back != 0 and prev_for_or_back != for_or_back and position.IR_output == 0:
            skip_count = True

        if position.IR_output == 1:
            if skip_count:
                skip_count = False
                print("skip count")
            else:
                motor_status = motor.status
                position.count_position(motor_status)

                motor.move(0)
                print("stop at location point briefly")

                time.sleep(3)
                motor.move(for_or_back)

        # Check the condition to redo the actions for the current cell
        else:
            redo = True
            # print(
            #     "Redoing actions for cell:",
            #     cell,
            #     "IR output:",
            #     position_object.IR_output,
            # )
            motor.move(for_or_back)
            # time.sleep(0.1)
        prev_for_or_back = for_or_back


# start thread for updating current location
threading.Thread(target=UpdateCurrentLocation).start()

while True:
    try:
        while True:
            motor.move(1)
            for_or_back = 1
            time.sleep(10)
            motor.move(0)
            for_or_back = 0
            time.sleep(1)
            motor.move(2)
            for_or_back = 2
            time.sleep(10)
            motor.move(0)
            for_or_back = 0
            time.sleep(1)
    except KeyboardInterrupt:
        motor.cleanup()
        position.cleanup()
