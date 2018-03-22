#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep
from helper import LargeMotorPair
import ev3dev.ev3 as ev3
from collections import deque
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


black_count = 1

black_average = 10
white_average = 0
black_stdev = 5
white_stdev = 0



SAMPLE_COUNT = 10

samples = deque([])
lcd = Screen()

def print_stuff(text, time = 0):
    lcd.clear()
    lcd.draw.text((36, 80), text)
    lcd.update()
    sleep(time)


def moveForward(speed = 100, len = 360):
    #if not pair.is_running:
    pair.run_to_rel_pos(speed_sp = speed * speedMult, position_sp = len)
    Leds.set_color(Leds.LEFT, Leds.GREEN)


def rotate(angle):
    mC.run_to_rel_pos(speed_sp = 100 * speedMult, position_sp = angle * 3)
    mB.run_to_rel_pos(speed_sp = 100 * speedMult, position_sp=-angle * 3)

def sample():
    return cl.value()

def calc_av(samples):
    if(len(samples) == 0):
        return 0
    av = 0
    for sample in samples:
        av += sample
    av = av / len(samples)
    return av

def push_sample(sample, max_samples = SAMPLE_COUNT):
    global samples
    while (len(samples) >= max_samples):
        samples.popleft()
    samples.append(sample)

def calc_stdev(samples, av):
    var = 0
    for sample in samples:
        var += (sample - av) ** 2
    var = var / (len(samples) - 1)
    stdev = var ** 0.5
    return stdev

def is_on_black(average):
    global samples
    if average < black_average + 2*black_stdev:
        return True
    return False

def is_on_white(average):
    global samples
    if average > white_average - 2*white_stdev:
        return True
    return False

def calc_current():
    this_samples = []
    for i in range(SAMPLE_COUNT):
        this_samples.append(sample())
    this_av = calc_av(this_samples)
    this_stdev = calc_stdev(this_samples, this_av)
    return (this_av, this_stdev)

average = 0
stdev = 0

black_tile_count = 0

def rotate(angle):
    mC.run_to_rel_pos(speed_sp = 100 * speedMult, position_sp = angle * 3)
    mB.run_to_rel_pos(speed_sp = 100 * speedMult, position_sp=-angle * 3)

def move_to_next_black():
    global black_tile_count
    on_black = True
    moveForward(50, 360)
    while(pair.is_running):
        (av,std) = calc_current()
        print_stuff("READING: "+str(av))
        if is_on_white(av) and on_black:
            on_black = False
        if not on_black:
            print_stuff("ON WHITE")
        if is_on_black(av) and not on_black:
            black_tile_count += 1
            pair.stop()
            Sound.beep()
            return True
    return False


def sweep(angle, steps = 30):
    step = angle/steps
    count = 0
    for i in range(steps):
        rotate(step)
        count += 1
        (av, stdev) = calc_current()
        if is_on_white(av):
            break

    rotate(-count*step)
    if count == steps -1:
        return 0
    return step * count

def sweep_check():
    #we are on a black tile, sweep for a white tile
    valL = sweep(-90)
    valR = sweep(90)
    val = valL + 90 if abs(valL) < abs(valR) else valR - 90
    rotate(val/3)


btn = Button()

try:
    while True:
        if move_to_next_black():
            sweep_check()
        if black_tile_count == 15:
            for i in range(5):
                Sound.beep()
            break
except:
    import traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
    while not btn.any():
        pass











