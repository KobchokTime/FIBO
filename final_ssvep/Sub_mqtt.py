import paho.mqtt.client as mqtt
import json

# MQTT parameters from the Tasmota configuration
MQTT_HOST = "192.168.1.108"
MQTT_PORT = 1883
MQTT_TOPIC = "tele/tasmota_01/SENSOR"  # Replace %06X with your device specific identifier if needed

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(f"Topic: {msg.topic} Message: {type(msg.payload.decode())}")
    parsed_data = json.loads(msg.payload.decode())
        # เข้าถึงค่า Current
    current_value = parsed_data['ENERGY']['Current']
    print("Current:", current_value)
            

# Create an MQTT client instance
client = mqtt.Client()

# Assign event callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(MQTT_HOST, MQTT_PORT, 60)

# Start a network loop
client.loop_forever()
