import threading
from time import sleep
import matplotlib
matplotlib.use('Agg')  # เลือกใช้ backend non-interactive เพื่อลดปัญหา GUI
import matplotlib.pyplot as plt
import numpy as np
import flet as ft
import io
import base64
from pylsl import StreamInlet, resolve_stream
from scipy.signal import welch

class GraphControl(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.running = False
        self.data_buffer = []

    def did_mount(self):
        self.running = True
        self.graph_thread = threading.Thread(target=self.update_graph, daemon=True)
        self.eeg_thread = threading.Thread(target=self.receive_eeg_data, daemon=True)
        self.graph_thread.start()
        self.eeg_thread.start()

    def will_unmount(self):
        self.running = False

    def update_graph(self):
        while self.running:
            if len(self.data_buffer) > 0:
                raw_data = self.data_buffer.pop(0)
                selected_channels = ['FP1', 'FP2', 'C3']  # เลือกช่องที่ต้องการพล็อต
                channels = ['FP1', 'FP2', 'C3', 'C4', 'T5', 'T6', 'O1', 'O2']
                
                plt.figure(figsize=(10, 5))  # สร้างกราฟเพียงครั้งเดียว
                for selected_channel in selected_channels:
                    channel_index = channels.index(selected_channel)
                    f, Pxx = welch(raw_data[channel_index], fs=250, nperseg=len(raw_data[channel_index]))
                    psds_mean = np.mean(Pxx)

                    plt.plot(f, 10 * np.log10(Pxx), label=f'{selected_channel}')  # เพิ่ม label ให้แต่ละช่อง

                plt.xlabel('Frequency (Hz)')
                plt.ylabel('Power Spectral Density (dB)')
                plt.title('PSD of EEG Channels (6-50 Hz)')
                plt.legend()
                plt.xlim([6, 50])

                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                data = base64.b64encode(buf.read()).decode()

                self.graph_control.src_base64 = data
                self.update()
                plt.close()
            sleep(1)


    def receive_eeg_data(self):
        num_samples = 100
        target_stream_name = 'obci_eeg1'
        All_streams = resolve_stream()
        EEG_streams = [stream for stream in All_streams if stream.name() == target_stream_name]

        if len(EEG_streams) == 0:
            print("Error: EEG stream not found")
            return

        inlet = StreamInlet(EEG_streams[0])

        while self.running:
            samples = []
            for i in range(num_samples):
                sample, timestamp = inlet.pull_sample()
                samples.append(sample)
            self.data_buffer.append(np.array(samples).T)
            sleep(1)

    def build(self):
        self.graph_control = ft.Image()
        return self.graph_control

def main(page: ft.Page):
    graph_control = GraphControl()
    page.add(graph_control)

    graph_control.did_mount()

ft.app(target=main, view = ft.WEB_BROWSER)
