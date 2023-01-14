import random
import os
import json

from pixel_ring import pixel_ring
from paho.mqtt import client as mqtt_client
from dotenv import load_dotenv
from pathlib import Path
from gpiozero import LED

power = LED(5)
power.on()

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

broker = os.environ.get('BROKER')
port = int(os.environ.get('PORT'))
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
client_id = f'python-mqtt-{random.randint(0, 100)}'

start_listening_topic = 'hermes/asr/startListening'
stop_listening_topic = 'hermes/asr/stopListening'


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        # https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(start_listening_topic)
        client.subscribe(stop_listening_topic)
    else:
        print("Failed to connect, return code %d\n", rc)


def on_message(client, userdata, msg):
    msg_payload_json = msg.payload.decode()
    print(f"Received `{msg_payload_json}` from `{msg.topic}` topic")
    msg_payload = {}
    try:
        msg_payload = json.loads(msg_payload_json)
    except Exception as e:
        print(e)
        return
    if msg.topic == start_listening_topic:
        pixel_ring.wakeup()
    if msg.topic == start_listening_topic:
        pixel_ring.off()


def connect_mqtt() -> mqtt_client:
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    print(f"Connecting to broker \"{broker}\"...\n")
    client.connect(broker, port)
    return client


def run():
    pixel_ring.set_brightness(10)
    client = connect_mqtt()
    client.loop_forever()


if __name__ == '__main__':
    run()
