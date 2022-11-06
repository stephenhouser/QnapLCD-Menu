# QnapLCD-Menu

A simplistic package and examples using the front panel display and buttons
on QNAP NAS devices under other operating systems. Tested with TVS-671,
but should work on other models that use the "A125" display with two buttons.

# What's Included

* *lcd-menu.py* a Python script that will display a menu similar to the default QNAP menu, written for TrueNAS SCALE but may work with other TrueNAS and FreeNAS systems.

* *qnaplcd* Python package (class) for using the front-panel (A125) display. Uses *pyserial* and threading to send button events to calling program.

# Installation

To install, clone this repository onto your NAS somewhere that is accessible to the admin (root) user. It needs to be run *as root* to communicate with the display and the TrueNAS CLI.

To communicate with the display, *pyserial* is required. If you are able to install it with `pip`, that's wonderful, do that!

```
pip3 install pyserial
```

If you are not able to (TrueNAS SCALE), you can use the included `setup.sh` script to install it into the current directory. In the *same directory* as `qnaplcd` (e.g. the root of this project)

```
./setup.sh
```

# Using

Add `lcd-menu.py` in TrueNAS SCALE under *System Settings*, *Advanced*, *Init/Shutdown Scripts* as a pre or post init script.

