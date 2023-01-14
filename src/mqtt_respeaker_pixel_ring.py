import random
import os
import json
import time
import threading
import signal

from paho.mqtt import client as mqtt_client
from dotenv import load_dotenv
from pathlib import Path
from pixel_ring import pixel_ring
from gpiozero import LED

power = LED(5)
power.on()
threads = []
client = None

SHOULD_TERMINATE = False
light_state = "off"
last_light_state = "off"

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

broker = os.environ.get('BROKER')
port = int(os.environ.get('PORT'))
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
client_id = f'python-mqtt-{random.randint(0, 100)}'

start_listening_topic = 'hermes/asr/startListening'
stop_listening_topic = 'hermes/asr/stopListening'
speak_topic = 'hermes/asr/speak'
think_topic = 'hermes/asr/think'


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        # https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(start_listening_topic)
        client.subscribe(stop_listening_topic)
        client.subscribe(speak_topic)
        client.subscribe(think_topic)
    else:
        print("Failed to connect, return code %d\n", rc)


def on_message(client, userdata, msg):
    if SHOULD_TERMINATE:
        return
    global light_state
    msg_payload_json = msg.payload.decode()
    print(f"Received `{msg_payload_json}` from `{msg.topic}` topic")
    msg_payload = {}
    try:
        msg_payload = json.loads(msg_payload_json)
    except Exception as e:
        print(e)
        return
    if msg.topic == start_listening_topic:
        light_state = "listen"
    if msg.topic == stop_listening_topic:
        light_state = "off"
    if msg.topic == speak_topic:
        light_state = "speak"
    if msg.topic == think_topic:
        light_state = "think"


def on_disconnect(client, userdata, rc):
    if not SHOULD_TERMINATE:
        client.reconnect()


def connect_mqtt() -> mqtt_client:
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    print(f"Connecting to broker \"{broker}\"...\n")
    client.connect(broker, port)
    return client


def light_state_thread():
    global last_light_state
    while not SHOULD_TERMINATE:
        try:
            if light_state is not last_light_state:
                print(
                    f"light_state: {light_state}, last_light_state: {last_light_state}")
                if light_state == "off":
                    pixel_ring.off()
                if light_state == "listen":
                    pixel_ring.listen()
                if light_state == "speak":
                    pixel_ring.speak()
                if light_state == "think":
                    pixel_ring.think()
                last_light_state = light_state
            time.sleep(0.1)
        except Exception as e:
            print(e)
    print("light_state_thread terminated")


def main_loop():
    while not SHOULD_TERMINATE:
        try:
            time.sleep(0.5)
        except Exception as e:
            print(e)
    print("main_loop terminated")


def exit_gracefully(signum, frame):
    global SHOULD_TERMINATE
    pixel_ring.off()
    time.sleep(1)
    power.off()
    if client is not None:
        client.disconnect()
        time.sleep(.1)
        client.loop_stop()
    SHOULD_TERMINATE = True


def run():
    global threads
    global client

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    t1 = threading.Thread(target=light_state_thread, args=())
    threads.append(t1)
    t1.start()

    pixel_ring.set_brightness(10)
    client = connect_mqtt()
    client.loop_start()

    main_loop()


if __name__ == '__main__':
    run()
