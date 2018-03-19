#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep
from helper import LargeMotorPair
import math

# Connect EV3 color sensor.
cl = ColorSensor()
# Connect EV3 color sensor.
cl = ColorSensor()
pair = LargeMotorPair(OUTPUT_B, OUTPUT_C)
pair.reset()

mB = LargeMotor('outB')
mC = LargeMotor('outC')

speedMult = 2

def print_stuff(text):
    lcd = Screen()
    lcd.draw.text((36, 80), text)
    lcd.update()
    sleep(6)

samples = []

def moveForward(speed = 100, len = 360):
    #if not pair.is_running:
    pair.run_to_rel_pos(speed_sp = speed * speedMult, position_sp = len)
    Leds.set_color(Leds.LEFT, Leds.GREEN)


def sample():
    global total
    global samples
    val = cl.value()

    samples.append(val)

moveForward(10,60)
for i in range(1000):
    sample()
Sound.beep()

av = 0
for sample in samples:
    av += sample
av = av/len(samples)

var = 0
for sample in samples:
    var += (sample - av) ** 2
var = var/(len(samples )- 1)

stdev = var ** 0.5

print_stuff('Average: ' + str(av))
print_stuff('Stdev: '+str(stdev))