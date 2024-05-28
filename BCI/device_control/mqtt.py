import paho.mqtt.client as mqtt
import time

# Define the MQTT broker address and port
broker_address = "192.168.1.108"
broker_port = 1883
topic_pub = "cmnd/tasmota_01/Power"
topic_sub = "bci/freq"

# Callback function to handle incoming messages
def on_message(client, userdata, message):
    print(f"Received message: {message.payload.decode()} on topic {message.topic}")

# Create a new MQTT client instance
client = mqtt.Client()

# Attach the on_message callback function
client.on_message = on_message

# Connect to the broker
client.connect(broker_address, broker_port)

# Subscribe to the topic
client.subscribe(topic_sub)

# Start the loop to process received messages
client.loop_start()

# Publish messages in a loop
try:
    while True:
        message = (input(str("")))
        client.publish(topic_pub, message)
        print(f"Published message: {message}")
        time.sleep(5)  # Publish a message every 5 seconds
except KeyboardInterrupt:
    print("Exiting...")

# Stop the loop and disconnect from the broker
client.loop_stop()
client.disconnect()
