#!/usr/bin/env python3
import platform
import qnaplcd

lcd = qnaplcd.QnapLCD()
lcd.backlight(True)
lcd.reset()
lcd.clear()
lcd.write(0, [platform.node(), 'System Ready...'])
