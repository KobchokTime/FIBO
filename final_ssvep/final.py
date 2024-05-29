from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import pandas as pd
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

data = {
    'power_values': [],
    'time_total': []
}
df = pd.DataFrame(data)
csv_file = 'data.csv'
df.to_csv(csv_file, index=False)
print("create csv success")

app = Flask(__name__)

# MQTT parameters from the Tasmota configuration
MQTT_HOST = "192.168.1.108"
MQTT_PORT = 1883
SENSOR_TOPIC = "tele/tasmota_01/SENSOR"
STATE_TOPIC = "tele/tasmota_01/STATE"
MQTT_PUBLISH_TOPIC = "cmnd/tasmota_01/Power"

average_power = 0
time_total = 0

global state

# Initialize lists to store current values and timestamps
sensor_power_values = []  # watt
sensor_timestamps = []  # Timestamps for SENSOR data
state_value = 0  # Store STATE data values

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(SENSOR_TOPIC)
    client.subscribe(STATE_TOPIC)

# The callback for when a PUBLISH message is received from the server for SENSOR topic.
def on_message_sensor(client, userdata, msg):
    global state_value, sensor_power_values, sensor_timestamps, average_power, time_total
    if state == 'ON':
        csv_file = 'data.csv'
        df = pd.read_csv(csv_file)
        # print(len(sensor_power_values),len(sensor_timestamps))
        parsed_data = json.loads(msg.payload.decode())
        current_value = parsed_data['ENERGY']['Current']
        voltage_value = parsed_data['ENERGY']['Voltage']
        power = (voltage_value * current_value) * 0.01
        print(f"SENSOR Current: {current_value} | Voltage: {voltage_value} | Power: {power}")
        sensor_power_values.append(power)
        sensor_timestamps.append(time.strftime('%H:%M:%S'))
        state_value = 1
        new_data = {
                    'power_values': [power],
                    'time_total': [time.strftime('%H:%M:%S')]
                    }
        new_row = pd.DataFrame(new_data)
        df = df._append(new_row, ignore_index=True)
        df.to_csv(csv_file, index=False)

    elif state == 'OFF' and state_value == 1:
        start_time = datetime.strptime(sensor_timestamps[0], "%H:%M:%S")
        end_time = datetime.strptime(sensor_timestamps[-1], "%H:%M:%S")
        average_power = sum(sensor_power_values) / (len(sensor_power_values) - 1)
        time_total = (end_time - start_time).total_seconds()
        print(f'\nPlug turn off => averagr power: {average_power} | time_total: {time_total/3600} hour | Energy consumption {average_power*(time_total/3600)} kwh')
        state_value = 0
        sensor_power_values = []  # watt
        sensor_timestamps = []

    elif state == 'OFF' and state_value == 0:
        print('Plug turn off')
    

# The callback for when a PUBLISH message is received from the server for STATE topic.
def on_message_state(client, userdata, msg):
    global state
    parsed_data1 = json.loads(msg.payload.decode())
    state = parsed_data1['POWER']
    pass

# Create an MQTT client instance
client = mqtt.Client()

# Assign event callbacks
client.on_connect = on_connect
client.message_callback_add(SENSOR_TOPIC, on_message_sensor)
client.message_callback_add(STATE_TOPIC, on_message_state)

# Connect to the MQTT broker
client.connect(MQTT_HOST, MQTT_PORT, 60)

# Start a network loop
client.loop_start()

@app.route('/')
def index():
    return render_template('final.html')

@app.route('/button1', methods=['POST'])
def button1():
    publish.single(MQTT_PUBLISH_TOPIC, "on", hostname=MQTT_HOST, port=MQTT_PORT)
    return "Button 1 clicked and MQTT message sent!"

@app.route('/button2', methods=['POST'])
def button2():
    publish.single(MQTT_PUBLISH_TOPIC, "off", hostname=MQTT_HOST, port=MQTT_PORT)
    return "Button 2 clicked and MQTT message sent!"

@app.route('/update_plot')
def update_plot():
    global average_power, time_total

    csv_file = 'data.csv'
    df = pd.read_csv(csv_file)
    # Prepare data for plotting
    p = df['power_values'].tolist()
    t = df['time_total'].tolist()
    # print(type(p))
    x = sensor_timestamps
    y = sensor_power_values
    message = f'average power: {round(average_power, 2)} | time total: {round(time_total/3600,2)} hours | Energy consumption: {round(average_power*(time_total/3600),2)} kWh'
    
    return jsonify({'x': t, 'y': p, 'message': message})

if __name__ == '__main__':
    app.run(debug=True)
