import socket
import threading
import time
from pylsl import resolve_stream, StreamInlet
from queue import Queue
from scipy.signal import welch
from joblib import load
import numpy as np
from keras.models import load_model
import paho.mqtt.client as mqtt

broker_address = "192.168.1.108"
broker_port = 1883
topic_pub = "bci/freq"

client = mqtt.Client()
client.connect(broker_address, broker_port, 60)
client.loop_start()

class EEGReceiver:
    def __init__(self):
        self.data_queue = Queue()
        self.running = True
        self.ready_for_processing = False
        self.start_time = None
        self.samples_buffer = []  # Initialize the samples buffer

    def receive_eeg_data(self):
        target_samples = 1500  # 1500 samples
        num_samples_per_iteration = 250  
        target_stream_name = 'obci_eeg1'

        while True:
            print("Searching for streams...")
            All_streams = resolve_stream()
            EEG_streams = [stream for stream in All_streams if stream.name() == target_stream_name]

            if len(EEG_streams) == 0:
                print("Error: No EEG stream found.")
                time.sleep(5)  # Wait for 5 seconds before trying to reconnect
                continue

            print(f"EEG stream '{target_stream_name}' found.")
            inlet = StreamInlet(EEG_streams[0])
            
            while True:
                try:
                    samples = []
                    for i in range(num_samples_per_iteration):
                        sample, timestamp = inlet.pull_sample(timeout=1.0)
                        if sample is None:
                            raise Exception("Stream disconnected")
                        samples.append(sample)

                    if samples:
                        self.samples_buffer.append(np.array(samples).T)
                    
                    if len(self.samples_buffer) > 0:
                        all_samples = np.hstack(self.samples_buffer)
                        if all_samples.shape[1] >= target_samples:
                            self.data_queue.put(all_samples[:, :target_samples])
                            self.samples_buffer = [all_samples[:, -750:]]
                            self.ready_for_processing = True

                except Exception as e:
                    print("Error: Stream disconnected. Attempting to reconnect...")
                    self.samples_buffer = []
                    self.ready_for_processing = False
                    break

    def process_data(self):
        rf_model = load('../model_FFT/best_rf_classifier.joblib')
        # svm_model = load('../model_FFT/best_svm_classifier_youtube.joblib')
        lda_model = load('../model_FFT/best_lda_classifier.joblib')
        knn_model = load('../model_FFT/best_knn_classifier.joblib')

        ann_model = load_model("../model_FFT/ann_model.h5")
        cnn_model = load_model("../model_FFT/cnn_model.h5")
        lstm_model = load_model("../model_FFT/lstm_model.h5")
        cnn_scaler = load("../model_FFT/cnn_scaler.pkl")
        lstm_scaler = load("../model_FFT/lstm_scaler.pkl")

        while True:
            if self.ready_for_processing and not self.data_queue.empty():
                data = self.data_queue.get()
                data = data[0:4,:]
                data_oz = data[0] - data[1]
                data_o1 = data[2] - data[1]
                data_o2 = data[3] - data[1]
                data_fft_oz = []
                data_fft_o2 = []
                data_fft_o1 = []
                
                f, Pxx = welch(data_oz, fs=250, nperseg= 250*4)
                data_fft_oz.append(Pxx[0:121])

                f, Pxx = welch(data_o1, fs=250, nperseg= 250*4)
                data_fft_o1.append(Pxx[0:121])

                f, Pxx = welch(data_o2, fs=250, nperseg= 250*4)
                data_fft_o2.append(Pxx[0:121])

                combined = np.hstack((data_fft_oz, data_fft_o1, data_fft_o2))
                
                pre_rf = rf_model.predict(combined)
                # pre_svm = svm_model.predict(combined)
                pre_lda = lda_model.predict(combined)
                pre_knn = knn_model.predict(combined)

                print(f'pre_rf => {pre_rf}')
                # print(f'pre_svm => {pre_svm}')
                print(f'pre_lda => {pre_lda}')
                print(f'pre_knn => {pre_knn}')

                # Normalize data with Scaler
                combined_test_scaled_cnn = cnn_scaler.transform(combined)
                combined_test_scaled_lstm = lstm_scaler.transform(combined)

                # Adapt data to the format used with the CNN model
                combined_test_reshaped_cnn = combined_test_scaled_cnn.reshape(-1, 363, 1)

                y_pred_ann = np.argmax(ann_model.predict(combined), axis=1)
                y_pred_cnn = np.argmax(cnn_model.predict(combined_test_reshaped_cnn), axis=1)

                # Adapt data to the format used with the LSTM model
                combined_test_reshaped_lstm = combined_test_scaled_lstm.reshape(-1, 363, 1)

                y_pred_lstm = np.argmax(lstm_model.predict(combined_test_reshaped_lstm), axis=1)

                print(f'pre_ann => {y_pred_ann}')
                print(f'pre_cnn => {y_pred_cnn}')
                print(f'pre_lstm => {y_pred_lstm}')
                print('--------------------------------------------------------------------------------')
                if y_pred_cnn == 0:
                    client.publish(topic_pub, "6")
                elif y_pred_cnn == 1:
                    client.publish(topic_pub, "20")
                
                self.ready_for_processing = False

receiver = EEGReceiver()

eeg_thread = threading.Thread(target=receiver.receive_eeg_data, daemon=True)
eeg_thread.start()

processing_thread = threading.Thread(target=receiver.process_data, daemon=True)
processing_thread.start()

while True:
    pass
