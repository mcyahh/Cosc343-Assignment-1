#!/usr/bin/env python3


from helper import LargeMotorPair
import logging
import math
import os
import re
import sys
import time

from ev3dev.ev3 import *

pair = LargeMotorPair(OUTPUT_B, OUTPUT_C)
pair.reset()

mB = LargeMotor('outB')
mC = LargeMotor('outC')

ts = TouchSensor()

# Connect EV3 color sensor.
cl = ColorSensor()

# Put the color sensor into COL-REFLECT mode
# to measure reflected light intensity.
cl.mode='COL-REFLECT'
btn = Button() # will use any button to stop script

sweepAngle = 10
speedMult = 5

def doStop():
    return btn.any()

def isColliding():
    return True if ts.value() > 0.1 else False

def isOnTrack():
    if cl.value() < 30:
        return True
    else:
        return False

def lookForTrack():
    sweepSum = -5
    pair.stop()
    while (not isOnTrack()) and not doStop() and not isColliding():
        if not (mC.is_running):
            sweepSum *= -2
            rotate(sweepSum)

def goAround(backup = 300, deviation = 800, angle = 30/1.5):
    Leds.set_color(Leds.LEFT, Leds.YELLOW)
    moveForward(200, -backup)
    pair.wait_until_not_moving()
    rotate(angle)
    mC.wait_until_not_moving()
    moveForward(100,deviation)
    pair.wait_until_not_moving()
    rotate(-2*angle)
    mC.wait_until_not_moving()
    while(not isOnTrack()):
        Leds.set_color(Leds.LEFT, Leds.AMBER)
        moveForward()
    rotate(1 * angle)
    mC.wait_until_not_moving()
    Leds.all_off()


def rotate(angle):
    mC.run_to_rel_pos(speed_sp = 100 * speedMult, position_sp = angle * 3)
    mB.run_to_rel_pos(speed_sp = 100 * speedMult, position_sp=-angle * 3)


def moveForward(speed = 100, len = 360):
    #if not pair.is_running:
    pair.run_to_rel_pos(speed_sp = speed * speedMult, position_sp = len)
    Leds.set_color(Leds.LEFT, Leds.GREEN)

Leds.all_off()

while (not btn.any()):
    time.sleep(0.1)
time.sleep(.5)
while True :
    if doStop():
        break

    if isOnTrack():
        moveForward()
    else:
        lookForTrack()
    if isColliding():
        goAround()

pair.stop()
Leds.set_color(Leds.LEFT, Leds.RED)