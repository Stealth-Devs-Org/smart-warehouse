import time

import Position

position_object = Position.Position()
while True:
    if position_object.detect_IR_W2B_change():
        print(f"IR output: {position_object.IR_output}")
    else:
        continue
    time.sleep(0.1)
