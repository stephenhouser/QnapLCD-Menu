#
# QNAP LCD Display and Button Class
#
import serial
from threading import *

# Get ID       send=0x4d, 0x00  recv=0x53, 0x01, 0xXX, 0xYY 
# Get Button   send=0x4d, 0x06  recv=0x53, 0x05, 0xXX, 0xYY
# Get Protocol send=0x4d, 0x07  recv=0x53, 0x08, 0xXX, 0xYY
# Display Char send=0x4d, 0x0C
# Display Cls  send=0x4d, 0x0D
# Backlight    send=x04d, 0x5e, 0xXX  : on,x=0x01 off,x=0x00
# Negative ACK                  recv=0x53, 0xFB, 0xXX
# Reset        send=0x4d, 0xFF

class QnapLCD:
    def __init__(self, port='/dev/ttyS1', speed=1200, handler=None):
        self.port = port
        self.speed = speed

        self.lines = 2
        self.columns = 16

        try:
            self.connection = serial.Serial(self.port, self.speed, timeout=None)
        except serial.SerialException as se:
            self.connection = None
            print('error', se)

        if handler:
            self.handler = handler
            self.reader = Thread(target=self.serial_reader)
            self.reader.start()

    def _read_bytes(self, bytes=1):
        if self.connection:
            data = self.connection.read(bytes)
            if bytes == 1:
                return data[0]

            return data

        return None

    def serial_reader(self):
        while True:
            preamble = self._read_bytes()
            if preamble == 0x53 or preamble == 0x83:
                cmd =  self._read_bytes()
                if cmd == 0x01:
                    report = self._read_bytes(2)
                    report = report[0] * 256 + report[1]
                    self.handler('Report_ID', report)

                if cmd == 0x05:
                    buttons = self._read_bytes(2)
                    buttons = buttons[0]*256 + buttons[1]
                    self.handler('Switch_Status', buttons)

                if cmd == 0x08:
                    version = self._read_bytes(2)
                    version = version[0]*256 + version[1]
                    self.handler('Protocol_Version', version)

                if cmd == 0xAA:
                    self.handler('Reset_OK', True)

                if cmd == 0xFA:
                    #self.buffer = sport.read()
                    self.handler('Ack', None)

                if cmd == 0xFB:
                    nack_cmd = self._read_bytes()
                    self.handler('Nack', nack_cmd)

    def backlight(self, on=True):
        if self.connection:
            if on:
                self.connection.write(bytes([0x4d, 0x5e, 0x01]))
            else:
                self.connection.write(bytes([0x4d, 0x5e, 0x00]))

    def clear(self):
        if self.connection:
            self.connection.write(bytes([0x4d, 0x0d]))

    def reset(self):
        if self.connection:
            self.connection.write(bytes([0x4d, 0xff]))

    def get_board(self):
        if self.connection:
            self.connection.write(bytes([0x4d, 0x00]))

    def get_protocol(self):
        if self.connection:
            self.connection.write(bytes([0x4d, 0x07]))

    def get_buttons(self):
        if self.connection:
            self.connection.write(bytes([0x4d, 0x06]))

    def write(self, line, msg):
        # line is 1 or 2
        if isinstance(msg, list):
            self.write(1, msg[0] if len(msg) >= 1 else '')
            self.write(2, msg[1] if len(msg) >= 2 else '')
        else:
            print(f'LINE {line}: {msg}')
            msg = msg[:self.columns]
            line %= 2
            line = 0x00 if line else 0x01
            if self.connection:
                self.connection.write(bytes([0x4d, 0x0c, line, len(msg)]))
                self.connection.write(msg.encode('utf-8'))
