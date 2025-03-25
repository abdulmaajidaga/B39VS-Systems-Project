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

kit.servo[0].angle = 20
kit.servo[3].angle = 140

time.sleep(1)
# kit.servo[0].angle = 40
# kit.servo[3].angle = 130

# time.sleep(0.6)
# kit.servo[0].angle = 60
# kit.servo[3].angle = 120

# time.sleep(0.6)
# kit.servo[0].angle = 80
# kit.servo[3].angle = 105

# time.sleep(0.6)
# kit.servo[0].angle = 85
# kit.servo[3].angle = 55


time.sleep(0.6)


