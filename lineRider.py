#!/usr/bin/env python3


from helper import LargeMotorPair
from collections import deque
import logging
import math
import os
import re
import sys
from time import sleep

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
speedMult = 2


lcd = Screen()

def print_stuff(text, time = 6):
    lcd.clear()
    lcd.draw.text((36, 80), text)
    lcd.update()
    sleep(time)

def doStop():
    return btn.any()

def isColliding():
    return True if ts.value() > 0.1 else False


samples = deque([])

def sample():
    return cl.value()

black_average = 10
black_stdev = 5

white_average = 45
white_stdev = 0

def calc_av(samples):
    if(len(samples) == 0):
        return 0
    av = 0
    for sample in samples:
        av += sample
    av = av / len(samples)
    print_stuff("Average "+str(av),0)
    return av

def push_sample(sample, max_samples = 10):
    global samples
    while (len(samples) >= max_samples):
        samples.popleft()
    samples.append(sample)

def is_on_black(average):
    if average < black_average + 2*black_stdev:
        return True
    return False

def is_on_white(average):
    if average > white_average - 2*white_stdev:
        return True
    return False

def isOnTrack():
    for i in range(10):
        push_sample(sample())
    average = calc_av(samples)
    if is_on_black(average) or is_on_white(average):
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



try:
    Leds.all_off()
    while (not btn.any()):
        time.sleep(0.1)
    time.sleep(.5)
    while True:
        if doStop():
            break

        if isOnTrack():
            moveForward()
        else:
            lookForTrack()

        if isColliding():
            goAround()
except:
    import traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
    while not btn.any():
        pass

pair.stop()
Leds.set_color(Leds.LEFT, Leds.RED)