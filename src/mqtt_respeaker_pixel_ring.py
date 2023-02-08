import random
import os
import json
import time
import threading
import signal

from paho.mqtt import client as mqtt_client
from dotenv import load_dotenv
from pathlib import Path
import yaml
from pixel_ring import pixel_ring
from gpiozero import LED
import rule_engine

power = LED(5)
power.on()
threads = {}
client = None

SHOULD_TERMINATE = False
light_state = "off"
last_light_state = "off"

config = {}
inbound_rules = []

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

broker = os.environ.get('BROKER')
port = int(os.environ.get('PORT'))
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
client_id = f'python-mqtt-{random.randint(0, 100)}'

start_listening_topic = 'hermes/asr/startListening'
stop_listening_topic = 'hermes/asr/stopListening'
speak_topic = 'hermes/tts/say'
think_topic = 'rhasspy/asr/recordingFinished'


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
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
    try:
        msg_payload = json.loads(msg_payload_json)

        event = {
            "topic": msg.topic,
            "payload": msg_payload
        }

        inbound_rule = next(
            filter(lambda inbound_rule: inbound_rule["rule"].matches(event), inbound_rules), None)
        light_state_tmp = None
        if inbound_rule:
            light_state_tmp = inbound_rule.get("light_state")
        if light_state_tmp:
            light_state = light_state_tmp
    except Exception as e:
        print(e)
        return


def on_disconnect(client, userdata, rc):
    if not SHOULD_TERMINATE:
        print("MQTT client disconnected")


def connect_mqtt() -> mqtt_client:
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    print(f"Connecting to broker \"{broker}\"...")
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
            time.sleep(.1)
        except Exception as e:
            print(e)
    print("light_state_thread terminated")


def mqtt_client_thread():
    global client
    client = connect_mqtt()
    client.loop_forever()


def main_loop():
    while not SHOULD_TERMINATE:
        try:
            time.sleep(.5)
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


def setup_rules():
    global inbound_rules

    for inbound_rule_config in config["rules"]["inbound"]:
        inbound_rule = {
            "rule": rule_engine.Rule(inbound_rule_config["rule"]),
            "light_state": inbound_rule_config["light_state"]
        }
        inbound_rules.append(inbound_rule)


def run():
    global threads

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    with open('config.yaml', 'r') as f:
        global config
        config = yaml.safe_load(f)

    setup_rules()

    light_state_thread_instance = threading.Thread(
        target=light_state_thread, args=())
    threads["light_state"] = light_state_thread_instance
    light_state_thread_instance.start()

    mqtt_client_thread_inst = threading.Thread(
        target=mqtt_client_thread, args=())
    threads["mqtt_client"] = mqtt_client_thread_inst
    mqtt_client_thread_inst.start()

    pixel_ring.set_brightness(20)
    pixel_ring.change_pattern('echo')

    main_loop()


if __name__ == '__main__':
    run()
