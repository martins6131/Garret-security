import paho.mqtt.client as mqtt
import time, random

client = mqtt.Client()
client.connect("localhost", 1883, 60)

while True:
    if random.random() > 0.8:  # ~20% chance every 5s
        payload = "Motion detected!"
        client.publish("/sensors/motion", payload)
        print(f"Published: {payload}")
    time.sleep(5)
