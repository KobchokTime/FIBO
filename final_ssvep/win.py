from flask import Flask, render_template, request
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

app = Flask(__name__)

MQTT_HOST = "192.168.1.108"
MQTT_PORT = 1883
MQTT_PUBLISH_TOPIC = "cmnd/tasmota_01/Power"
MQTT_SUBSCRIBE_TOPIC = "stat/tasmota_01/POWER"

# Callback Function on MQTT Message Received
def on_message(client, userdata, message):
    print(f"Received message: {str(message.payload.decode('utf-8'))}")

client = mqtt.Client()
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.subscribe(MQTT_SUBSCRIBE_TOPIC)
client.on_message = on_message
client.loop_start()

@app.route('/')
def home():
    return render_template('win.html')


@app.route('/button1', methods=['POST'])
def button1():
    publish.single(MQTT_PUBLISH_TOPIC, "on", hostname=MQTT_HOST, port=MQTT_PORT)
    return "Button 1 clicked and MQTT message sent!"

@app.route('/button2', methods=['POST'])
def button2():
    publish.single(MQTT_PUBLISH_TOPIC, "off", hostname=MQTT_HOST, port=MQTT_PORT)
    return "Button 2 clicked and MQTT message sent!"

if __name__ == "__main__":
    app.run(debug=True)
