import random
import os
import json

from paho.mqtt import client as mqtt_client
from dotenv import load_dotenv
from pathlib import Path

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
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)


def connect_mqtt():
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, msg, topic):
    payload_str = json.dumps(msg)
    result = client.publish(topic, payload_str)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def run():
    client = connect_mqtt()
    client.loop_start()

    # publish(client, {"siteId": "satellite1"}, start_listening_topic)
    # time.sleep(10)
    # publish(client, {}, think_topic)
    # time.sleep(10)
    # publish(client, {}, speak_topic)
    # time.sleep(10)
    publish(client, {"siteId": "satellite1"}, stop_listening_topic)


if __name__ == '__main__':
    run()
