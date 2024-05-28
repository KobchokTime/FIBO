import paho.mqtt.client as mqtt
import time

broker_address = "192.168.1.108"
broker_port = 1883
topic_pub = "cmnd/tasmota_01/Power"
topic_sub = "bci/freq"

def on_message(client, userdata, message):
    received_message = message.payload.decode()
    print(f"Received message: {received_message} on topic {message.topic}")
    if received_message == "20":
        response_message = "on"
        client.publish(topic_pub, response_message)
        print(f"Published message: {response_message} to topic {topic_pub}")
    if received_message == "6":
        response_message = "off"
        client.publish(topic_pub, response_message)
        print(f"Published message: {response_message} to topic {topic_pub}")

client = mqtt.Client()

client.on_message = on_message

client.connect(broker_address, broker_port)

client.subscribe(topic_sub)

# Start the loop
client.loop_start()

# Publish messages in a loop
# try:
#     while True:
#         message = (input(str("")))
#         client.publish(topic_pub, message)
#         print(f"Published message: {message}")
#         time.sleep(5)  # Publish a message every 5 seconds
# except KeyboardInterrupt:
#     print("Exiting...")
# try:
#     while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("Exiting...")

client.loop_stop()
client.disconnect()
