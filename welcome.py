#!/usr/bin/env python3
import ev3dev.ev3 as ev3
from ev3dev.ev3 import *
from time import sleep

lcd = Screen()
lcd.draw.text((36,80),'THIS TEXT IS BLACK')
lcd.update()
sleep(6)