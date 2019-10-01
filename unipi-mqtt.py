#!/usr/bin/python3

import json
import logging
import logging.handlers
import paho.mqtt.client
import sys
import time
import traceback
import websocket

from threading import Timer,Thread,Event

# {"interval": 15, "value": 16.95, "circuit": "28409D1F0000801E", "address": "28409D1F0000801E", "time": 1569915680.064948, "typ": "DS18B20", "lost": false, "dev": "temp"}
# [{"circuit": "3_01", "value": 0, "glob_dev_id": 1, "dev": "wd", "timeout": 5000, "was_wd_reset": 0, "nv_save": 0}, {"circuit": "2_01", "value": 0, "glob_dev_id": 1, "dev": "wd", "timeout": 5000, "was_wd_reset": 0, "nv_save": 0}]


logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.DEBUG)
mylog = logging.getLogger('MyLogger')
# handler = logging.handlers.SysLogHandler(address = '/dev/log')
#mylog.addHandler(handler)


def on_log(client, userdata, level, buf):
    mylog.debug("[MQTT]ONLOG: %s, %s, %s, %s" % (client, userdata, level, buf))

def on_ws_message(ws, message):
    obj = json.loads(message)
    mylog.debug('[WS_IN]: %s' % (message))
    if type(obj) is not list:
        obj = [obj]
    for single_obj in obj:
        dev = single_obj['dev']
        circuit = single_obj['circuit']
        value = single_obj['value']
        mylog.info("[WEBSOCKET]Value: " + str(value) + " Device: " + str(dev) + " Circuit: " + str(circuit))
        mqtt.publish('test/%s/%s' % (str(dev), str(circuit)), str(value))
  
def on_ws_error(ws, error):
    mylog.error("[WEBSOCKET]%s" % (error))

def on_ws_close(ws):
    mylog.info("[WEBSOCKET]Connection closed")
  
def on_ws_open(ws):
    # Turn on filtering
    ws.send(json.dumps({"cmd":"filter", "devices":["sensor", "input", "relay", "ao", "led"]}))
    # Turn on DO 1.01
    # ws.send(json.dumps({"cmd":"set", "dev":"relay", "circuit": "1_01", "value":1}))
    # Query for complete status
    ws.send(json.dumps({"cmd":"all"}))

def on_mqtt_connect(client, userdata, flags, rc):
    mylog.info("[MQTT]Connected with result code "+str(rc))

    #client.subscribe("homeassistant/cover/#")

def on_mqtt_disconnect(client, userdata, rc):
    mylog.info("[MQTT]Disconnected")

if __name__ == "__main__":
    devices = []
    url = "ws://192.168.88.32:8080/ws"
    ws = websocket.WebSocket()

    mqtt = paho.mqtt.client.Client(client_id='unipi-mqtt-gateway')
    mqtt.on_connect = on_mqtt_connect
    mqtt.on_disconnect = on_mqtt_disconnect
    #mqtt.on_log = on_log
    mqtt.enable_logger(mylog)
    mqtt.connect("192.168.88.33", 1883, 60)

    #receiving messages
    ws = websocket.WebSocketApp(url, on_open = on_ws_open, on_message = on_ws_message, on_error = on_ws_error, on_close = on_ws_close)

    mqtt.loop_start()
    ws.run_forever()
    mylog.debug("WS stopped")

    mqtt.disconnect()
    mqtt.loop_stop(force=False)
