import paho.mqtt.client as mqtt

# MQTT parameters
MQTT_HOST = "192.168.1.108"
MQTT_PORT = 1883
MQTT_PUBLISH_TOPIC = "cmnd/tasmota_01/Power"
MQTT_PAYLOAD = "on"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Publishing a message to the topic with the given payload
    client.publish(MQTT_PUBLISH_TOPIC, MQTT_PAYLOAD)

# Create an MQTT client instance
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(MQTT_HOST, MQTT_PORT, 60)

# Start a network loop
client.loop_start()

# Publish the message
client.publish(MQTT_PUBLISH_TOPIC, MQTT_PAYLOAD)

# Stop the loop after publishing
client.loop_stop()
