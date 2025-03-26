# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries

# SPDX-License-Identifier: MIT


"""Simple test for a standard servo on channel 0 and a continuous rotation servo on channel 1."""

import time

from adafruit_servokit import ServoKit
import sys


# Set channels to the number of servo channels on your kit.

# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.

kit = ServoKit(channels=16)

# motor 0 - [0 95]

# picking 
# 0: 20 - 85
# 3: 140 - 55

# while True:
#     kit.servo[int(sys.argv[1])].angle = int(input())

if sys.argv[1] == "0":
    kit.servo[1].angle = 20
    kit.servo[2].angle = 140
    kit.servo[3].angle = 0
    kit.servo[0].angle = 0
elif sys.argv[1] == "1":
    kit.servo[1].angle = 85
    kit.servo[2].angle = 55
    time.sleep(0.6)
    kit.servo[3].angle = 38
elif sys.argv[1] == "2":
    kit.servo[1].angle = 20
    kit.servo[2].angle = 140
    kit.servo[3].angle = 38
elif sys.argv[1] == "3":
    kit.servo[1].angle = 85
    kit.servo[2].angle = 55
    kit.servo[3].angle = 38
    time.sleep(0.6)
    kit.servo[3].angle = 0


time.sleep(0.6)


