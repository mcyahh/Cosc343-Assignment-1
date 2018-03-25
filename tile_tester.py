#!/usr/bin/env python3
from ev3dev.ev3 import *
from time import sleep
from helper import LargeMotorPair

from collections import deque
import math
btn = Button()
# Connect EV3 color sensor.
cl = ColorSensor()
# Connect EV3 color sensor.
cl = ColorSensor()

ts = TouchSensor()
try:
    #Connect to sonar
    sn = UltrasonicSensor()
    assert sn.connected, "Connect a single US sensor to any sensor port"
    # Put the US sensor into distance mode.
    sn.mode='US-DIST-CM'
except:
    import traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
    while not btn.any():
        pass






pair = LargeMotorPair(OUTPUT_B, OUTPUT_C)
pair.reset()


mB = LargeMotor('outB')
mC = LargeMotor('outC')

speedMult = 2


black_count = 1

black_average = 10
white_average = 45
black_stdev = 5
white_stdev = 10


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


def sweep_sonar(angle, steps = 20):
    step = angle / steps
    count = 0
    min = float('inf')
    for i in range(steps):
        rotate(step,speed=20)
        pair.wait_until_not_moving(timeout=3000)
        sleep(0.1)
        dist = sn.value()
        if dist<min:
            count = i
            min = dist
        print_stuff("Min Step: "+str(count) + " Min: "+str(min))
    for i in range(steps):
        rotate(-step, speed=20)
        sleep(0.1)
        pair.wait_until_not_moving(timeout=3000)
    #pair.wait_until_not_moving(timeout=3000)
    return (count * step, min)

def sweep_sonar_smooth(angle):
    rotate(angle)
    maxcount = 0
    count_point = 0
    min = float('inf')
    while pair.is_running:
        maxcount += 1
        dist = sn.value()
        if dist < min:
            min = dist
            count_point = maxcount
        print_stuff("CP, MC: " + str(count_point) + " , " + str(maxcount))
        sleep(0.01)

    rotate(-angle)
    pair.wait_until_not_moving()
    print_stuff("CP, MC: "+ str(count_point) + " , " + str(maxcount))
    return ((float(count_point)/float(maxcount)) * angle, min)

def sonar_find_min():
    Sound.beep()
    (langle, lval) = sweep_sonar(-45)
    (rangle, rval) = sweep_sonar(45)
    angle = langle if lval < rval else rangle

    if (angle == 0):
        return min(lval,rval)
    rotate(angle * 1.1)
    pair.wait_until_not_moving(timeout=3000)
    return min(lval,rval)

def rotate(angle, fwd = 0, speed = 50):
    mC.run_to_rel_pos(speed_sp = speed * speedMult, position_sp = angle * 3 + fwd)
    mB.run_to_rel_pos(speed_sp = speed * speedMult, position_sp=-angle * 3 + fwd)


def move_to_next_black():
    print_stuff("Moving")
    global black_tile_count
    on_black = True
    moveForward(100, 720)
    while(pair.is_running):
        (av,std) = calc_current()
        if is_on_white(av) and on_black:
            on_black = False
        if is_on_black(av) and not on_black:
            black_tile_count += 1
            pair.stop()
            #moveForward(200, 45)
            pair.wait_until_not_moving()
            Sound.speak(black_tile_count)
            return True
    return False


def sweep(angle, steps = 30):
    step = angle/steps
    count = 0
    for i in range(steps):
        rotate(step, 20)
        pair.wait_until_not_moving(timeout=3000)
        count += 1
        (av, stdev) = calc_current()
        if is_on_white(av):
            break
    for i in range(count):
        rotate(-step, -20)
        pair.wait_until_not_moving(timeout=3000)
    if count == steps -1:
        return angle
    return step * count


ROT_ = 180


def sweep_check():
    print_stuff("Sweeping")
    #we are on a black tile, sweep for a white tile
    valL = sweep(-ROT_)
    valR = sweep(ROT_)
    val = valL + valR
    if not val == 0:
        rotate(val/7)
        print_stuff("Val: "+str(val))
        pair.wait_until_not_moving(timeout=3000)


try:

    move_to_next_black()
    moveForward(50, 100)
    pair.wait_until_not_moving()
    rotate(-55)
    pair.wait_until_not_moving()
    moveForward(50,-120)
    pair.wait_until_not_moving()
    sweep_check()
    while True:
        if move_to_next_black():
            sweep_check()
        if black_tile_count == 15:
            for i in range(5):
                Sound.beep()
            break
    rotate(-55)
    pair.wait_until_not_moving()
    moveForward(400,4000)
    pair.wait_until_not_moving()


    seek_and_destroy = True
    while seek_and_destroy:
        #check if we even need to sweep
        if (sn.value()>60):
            val = sonar_find_min()
        else:
            val = 0
        print_stuff("MIN: " + str(val))
        Sound.beep()
        #if we are super close
        if val<60:
            seek_and_destroy = False
            Sound.speak("Prepare to die, bottle!")
            sleep(2)
        else:
            moveForward(200, 360)
            pair.wait_until_not_moving(timeout=3000)


    #reverse and ram
    moveForward(100,-90)
    pair.wait_until_not_moving(timeout=3000)
    # check if we are on white, if so, move onto black
    #if not sample()>black_average + black_stdev:
    #    move_to_next_black()
    moveForward(500,1080)
    sleep(0.5)
    #push till we are off black
    while pair.is_running:
        if sample()>black_average + black_stdev:
            pair.stop()
            break
    Sound.speak("Victory! Take that bottle!")
    sleep(3)

except:
    import traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
    while not btn.any():
        pass




