#!/usr/bin/env python3
import sys
import os
import time
import qnaplcd
import platform
import subprocess
import socket
import threading
import json

DISPLAY_TIMEOUT = 30    # seconds

PORT = '/dev/ttyS1'     # same as default
PORT_SPEED = 1200

lcd = None

lcd_timer = None
def lcd_on():
    global lcd_timer

    lcd.backlight(True)

    if lcd_timer:
        lcd_timer.cancel()

    lcd_timer = threading.Timer(DISPLAY_TIMEOUT, lambda: lcd.backlight(False))
    lcd_timer.start()

def shell(cmd):
    return subprocess.check_output(cmd, shell=True, universal_newlines=True).strip()

def show_version():
    sys_name = platform.node()
    sys_vers = f'{platform.system()} ({platform.machine()})'
    lcd.clear()
    lcd.write(0, [sys_name, sys_vers])

def show_truenas():
    truenas = shell('cli -c \'system version\'')
    truenas = truenas.split('-')

    lcd.clear()
    lcd.write(0, ['-'.join(truenas[:-1]), truenas[-1]])

def show_uptime():
    uptime = shell('uptime').split(',')
    up = ' '.join(uptime[0].split()[2:]) + ' ' + uptime[1]
    load = os.getloadavg()
    lcd.clear()
    lcd.write(0, [f'Up  : {up}', f'Load: {load[0]} {load[1]}, {load[2]}'])

ip_addresses = []
def add_ips_to_menu():
    def get_kind(iface):
        if 'linkinfo' in iface:
            if 'info_kind' in iface['linkinfo']:
                return iface['linkinfo']['info_kind']
            elif 'info_slave_kind' in iface['linkinfo']:
                return 'slave'

        return ''

    def get_details(iface, kind):
        if 'addr_info' in iface:
            if kind == 'slave':
                return iface['operstate']
            else:
                for addr in iface['addr_info']:
                    if addr['family'] == 'inet':
                        return addr['local']

        return '0.0.0.0'

    ip_json = json.loads(shell('ip -details -json address show'))
    ip_addresses.clear()
    for iface in ip_json:
        if iface['link_type'] == 'loopback':
            continue

        kind = get_kind(iface)
        if kind not in ['', 'tun', 'bond', 'slave']:
            continue

        ip_addresses.append(( iface['ifname'], get_details(iface, kind)))

    while show_ip in menu:
        menu.remove(show_ip)

    for _ in ip_addresses:
        menu.append(show_ip)

def show_ip():
    ip_index = 0
    for index in range(menu_item):
        if menu[index] == show_ip:
            ip_index += 1

    lcd.clear()
    lcd.write(0, [f'{ip_addresses[ip_index][0]}', f'{ip_addresses[ip_index][1]}'])

zfs_pools = []
def add_zpools_to_menu():
    pools = shell('zpool list').split('\n')

    zfs_pools.clear()
    for pool in pools[1:]:
        zfs_pools.append(pool.split())

    # remove existing zfs pool menu items
    while show_zpool in menu:
        menu.remove(show_zpool)

    # add zfs pool menu items for discovered pools
    for _ in zfs_pools:
        menu.append(show_zpool)

def show_zpool():
    pool_index = 0
    for index in range(menu_item):
        if menu[index] == show_zpool:
            pool_index += 1

    pool = zfs_pools[pool_index]

    lcd.clear()
    lcd.write(0, [f'{pool[0]} ({pool[7]})', f'{pool[2]} of {pool[1]}'])

#
# Menu
#
menu_item = 0
menu = [
    show_truenas,
    show_version,
    show_uptime
]

def response_handler(command, data):
    global menu_item, lcd_timeout
    prev_menu = menu_item

    #print(f'RECV: {command} - {data:#04x}')

    if command == 'Switch_Status':
        lcd_on()

        if data == 0x01: # up
            menu_item = (menu_item - 1) % len(menu)

        if data == 0x02: # down
            menu_item = (menu_item + 1) % len(menu)

    if prev_menu != menu_item:
        #print(f'SHOW: {menu_item}')
        menu[menu_item]()


def main():
    global lcd

    lcd = qnaplcd.QnapLCD(PORT, PORT_SPEED, response_handler)
    lcd_on()
    lcd.reset()
    lcd.clear()

    lcd.write(0, [platform.node(), 'System Ready...'])

    quit = False
    while not quit:
        add_ips_to_menu()
        add_zpools_to_menu()
        menu[menu_item]()

        print('sleep...')
        time.sleep(30)

    lcd.backlight(False)

main()