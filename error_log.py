#!/usr/bin/env python3
from ev3dev.ev3 import *
import time

def main():
    # remove the following line and replace with your code
    raise ValueError('A very specific bad thing happened.')

try:
    btn = Button()
    main()
except:
    import traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
    while not btn.any():
        pass
