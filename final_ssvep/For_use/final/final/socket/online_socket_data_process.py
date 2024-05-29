import socket
import threading
import time 
from pylsl import resolve_stream, StreamInlet, StreamInfo, StreamOutlet
from queue import Queue
from scipy.signal import welch
from joblib import load
import numpy as np
from datetime import datetime
from keras.models import load_model
import paho.mqtt.client as mqtt

broker_address = "mqtt-dashboard.com"
broker_port = 1883
topic_pub = "bci/freq"

client = mqtt.Client()
client.connect(broker_address, broker_port, 60)
client.loop_start()

class EEGReceiver:
    def __init__(self):
        self.data_queue = Queue()
        self.running = False
        self.ready_for_processing = False
        self.start_time = None

    def receive_eeg_data(self):
        target_duration = 4  # 6 seconds
        num_samples_per_iteration = 250  
        target_stream_name = 'obci_eeg1'

        while True:
            print("Searching for streams...")
            All_streams = resolve_stream()
            EEG_streams = [stream for stream in All_streams if stream.name() == target_stream_name]

            if len(EEG_streams) == 0:
                print("Error: No EEG stream found. Retrying in 5 seconds...")
                time.sleep(5)
                continue

            print(f"EEG stream '{target_stream_name}' found.")
            inlet = StreamInlet(EEG_streams[0])

            total_samples_collected = 0  
            samples_buffer = [] 
            state = 0
            while True:
                if state == 0 and self.running and len(samples_buffer) == 0 and total_samples_collected == 0:
                    print('Begin')
                    state = 1
                elif self.running and state == 1:
                    if self.start_time is None:
                        self.start_time = time.time()

                    samples = []
                    for i in range(num_samples_per_iteration):
                        try:
                            sample, timestamp = inlet.pull_sample(timeout=1.0)
                        except Exception as e:
                            print(f"Error receiving sample: {e}")
                            break

                        if sample is not None:
                            samples.append(sample)

                    if samples:
                        samples_buffer.append(np.array(samples).T)
                        total_samples_collected += len(samples)

                    current_time = time.time()
                    if current_time - self.start_time >= target_duration:
                        all_samples = np.hstack(samples_buffer)
                        self.data_queue.put(all_samples)
                        print("6 seconds have passed. Send information to the queue.")
                        total_samples_collected = 0 
                        samples_buffer = []  
                        self.ready_for_processing = True 
                        state = 0
                        self.running = False
                        self.start_time = None
                else:
                    break

    def process_data(self):
        rf_model = load('../model_FFT/best_rf_classifier_youtube.joblib')
        svm_model = load('../model_FFT/best_svm_classifier_youtube.joblib')
        lda_model = load('../model_FFT/best_lda_classifier_youtube.joblib')
        knn_model = load('../model_FFT/best_knn_classifier_youtube.joblib')

        ann_model = load_model("../model_FFT/ann_model_youtube.h5")
        cnn_model = load_model("../model_FFT/cnn_model_youtube.h5")
        lstm_model = load_model("../model_FFT/lstm_model_youtube.h5")
        cnn_scaler = load("../model_FFT/cnn_scaler_youtube.pkl")
        lstm_scaler = load("../model_FFT/lstm_scaler_youtube.pkl")

        while True:
            if self.ready_for_processing and not self.data_queue.empty():
                data = self.data_queue.get()
                data = data[0:4, :]
                data_oz = data[0] - data[1]
                data_o1 = data[2] - data[1]
                data_o2 = data[3] - data[1]
                data_fft_oz = []
                data_fft_o2 = []
                data_fft_o1 = []

                f, Pxx = welch(data_oz, fs=250, nperseg=250*4)
                data_fft_oz.append(Pxx[0:121])

                f, Pxx = welch(data_o1, fs=250, nperseg=250*4)
                data_fft_o1.append(Pxx[0:121])

                f, Pxx = welch(data_o2, fs=250, nperseg=250*4)
                data_fft_o2.append(Pxx[0:121])

                combined = np.hstack((data_fft_oz, data_fft_o1, data_fft_o2))

                # Measure time for Random Forest prediction
                start_time_rf = time.time()
                pre_rf = rf_model.predict(combined)
                end_time_rf = time.time()
                time_rf = end_time_rf - start_time_rf

                # Measure time for SVM prediction
                start_time_svm = time.time()
                pre_svm = svm_model.predict(combined)
                end_time_svm = time.time()
                time_svm = end_time_svm - start_time_svm

                # Measure time for LDA prediction
                start_time_lda = time.time()
                pre_lda = lda_model.predict(combined)
                end_time_lda = time.time()
                time_lda = end_time_lda - start_time_lda

                # Measure time for kNN prediction
                start_time_knn = time.time()
                pre_knn = knn_model.predict(combined)
                end_time_knn = time.time()
                time_knn = end_time_knn - start_time_knn

                print(f'pre_rf => {pre_rf}')
                print(f'pre_svm => {pre_svm}')
                print(f'pre_lda => {pre_lda}')
                print(f'pre_knn => {pre_knn}')

                print(f'Time taken for Random Forest prediction: {time_rf} seconds')
                print(f'Time taken for SVM prediction: {time_svm} seconds')
                print(f'Time taken for LDA prediction: {time_lda} seconds')
                print(f'Time taken for kNN prediction: {time_knn} seconds')

                # Normalize data with Scaler
                combined_test_scaled_cnn = cnn_scaler.transform(combined)
                combined_test_scaled_lstm = lstm_scaler.transform(combined)

                # Adapt data to the format used with the CNN model
                combined_test_reshaped_cnn = combined_test_scaled_cnn.reshape(-1, 363, 1)

                # Measure time for ANN prediction
                start_time_ann = time.time()
                y_pred_ann = np.argmax(ann_model.predict(combined), axis=1)
                end_time_ann = time.time()
                time_ann = end_time_ann - start_time_ann

                # Measure time for CNN prediction
                start_time_cnn = time.time()
                y_pred_cnn = np.argmax(cnn_model.predict(combined_test_reshaped_cnn), axis=1)
                end_time_cnn = time.time()
                time_cnn = end_time_cnn - start_time_cnn

                # Adapt data to the format used with the LSTM model
                combined_test_reshaped_lstm = combined_test_scaled_lstm.reshape(-1, 363, 1)

                # Measure time for LSTM prediction
                start_time_lstm = time.time()
                y_pred_lstm = np.argmax(lstm_model.predict(combined_test_reshaped_lstm), axis=1)
                end_time_lstm = time.time()
                time_lstm = end_time_lstm - start_time_lstm

                print(f'pre_ann => {y_pred_ann}')
                print(f'pre_cnn => {y_pred_cnn}')
                print(f'pre_lstm => {y_pred_lstm}')
                if y_pred_cnn == 0:
                    client.publish(topic_pub, "6")
                elif y_pred_cnn == 1:
                    client.publish(topic_pub, "20")

                print(f'Time taken for ANN prediction: {time_ann} seconds')
                print(f'Time taken for CNN prediction: {time_cnn} seconds')
                print(f'Time taken for LSTM prediction: {time_lstm} seconds')

                self.ready_for_processing = False

receiver = EEGReceiver()

eeg_thread = threading.Thread(target=receiver.receive_eeg_data, daemon=True)
eeg_thread.start()

processing_thread = threading.Thread(target=receiver.process_data, daemon=True)
processing_thread.start()

# ตั้งค่าที่อยู่ IP และพอร์ต
server_ip = '10.7.143.220'  # Listen on this IP address
server_port = 1000

# สร้าง socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# ผูก socket กับ IP และพอร์ต
server_socket.bind((server_ip, server_port))

# รอการเชื่อมต่อ
server_socket.listen(5)
print(f"Server is listening on {server_ip}:{server_port}")

# ฟังก์ชันในการจัดการ client ที่เชื่อมต่อ
def handle_client(client_socket):
    print("Connection from client has been established.")
    while True:
        try:
            # รับข้อมูลจาก client
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            print(f"Received data from client: {data}")
            if data == "receiver.running = True":
                receiver.running = True
        except ConnectionResetError:
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    print("Connection from client has been closed.")
    client_socket.close()

# รับการเชื่อมต่อจาก client
while True:
    client_socket, client_address = server_socket.accept()
    threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()
