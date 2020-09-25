#!/usr/bin/python3
#
# mpp2emoncms.py
# Written initally by Jean-Charles de Longueville <jean-charles@de-longueville.eu>
# to feed his openenergymonitor.org system
#
# script to query MPP Solar PIP-4048MS inverter/charger
# - inverter connected to computer via serial
#      (USB used for testing)
# - posts results to MQTT broker running on emonCMS
#      feeds will appear under serial_number of inverter as node ID
# - uses mpputils.py / mppcommands.py to abstract PIP communications
#
import paho.mqtt.publish as publish
from .mpputils import mppUtils

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='MPP Solar Inverter Info Utility')
    parser.add_argument('-d', '--device', type=str, help='Serial device(s) to communicate with [comma separated]', default='/dev/hidraw0')
    parser.add_argument('-M', '--model', type=str, help='Specifies the inverter model to select commands for, defaults to "standard", currently supports LV5048', default='standard')
    parser.add_argument('-b', '--baud', type=int, help='Baud rate for serial communications', default=2400)
    parser.add_argument('-q', '--broker', type=str, help='MQTT Broker hostname', default='emonpi')
    parser.add_argument('-u', '--username', type=str, help='MQTT Broker username', default='emonpi')
    parser.add_argument('-p', '--password', type=str, help='MQTT Broker password', default='emonpimqtt2016')
    args = parser.parse_args()

    # emonCMS exposes a mosquitto requiring auth
    if not args.username:
        auth = None
    else:
        auth = { 'username': '{}'.format(args.username), 'password':'{}'.format(args.password) }

    # Process / loop through all supplied devices
    for usb_port in args.device.split(','):
        mp = mppUtils(usb_port, args.baud, args.model)
        serial_number = mp.getSerialNumber()

        # Collect Inverter Status data and publish
        msgs = []
        fullStatus = mp.getFullStatus()
        for key in sorted(fullStatus):
            topic = 'emon/{}/{}'.format(serial_number, key)
            msg = {'topic': topic, 'payload': '{}'.format(fullStatus[key]['value'])}
            msgs.append(msg)
        publish.multiple(msgs, hostname=args.broker, auth=auth)
