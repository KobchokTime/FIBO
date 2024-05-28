import threading
from time import sleep
from pylsl import resolve_stream, StreamInlet
import numpy as np
from queue import Queue

class EEGReceiver:
    def __init__(self):
        self.data_queue = Queue()
        self.running = False
        self.ready_for_processing = False

    def receive_eeg_data(self):
        target_samples = 1000  # จำนวนตัวอย่างที่ต้องการสะสมก่อนประมวลผล
        num_samples_per_iteration = 250  # จำนวนตัวอย่างที่รับต่อการวนลูปแต่ละครั้ง
        target_stream_name = 'obci_eeg1'
        
        print("กำลังค้นหาสตรีม...")
        All_streams = resolve_stream()
        EEG_streams = [stream for stream in All_streams if stream.name() == target_stream_name]
        
        if len(EEG_streams) == 0:
            print("Error: ไม่พบสตรีม EEG")
            return
        
        print(f"พบสตรีม EEG '{target_stream_name}' แล้ว.")
        inlet = StreamInlet(EEG_streams[0])
        
        total_samples_collected = 0  # ตัวแปรเพื่อเก็บจำนวนตัวอย่างที่รับมาแล้ว
        samples_buffer = []  # บัฟเฟอร์เพื่อสะสมตัวอย่าง

        while self.running:
            samples = []
            for i in range(num_samples_per_iteration):
                sample, timestamp = inlet.pull_sample()
                if sample is not None:
                    samples.append(sample)
            
            if samples:
                samples_buffer.append(np.array(samples).T)
                total_samples_collected += len(samples)
                print(f"ได้รับ {len(samples)} ตัวอย่าง, ขนาดบัฟเฟอร์: {total_samples_collected}")
            
            # เช็คว่ามีตัวอย่างครบ 1000 หรือไม่
            if total_samples_collected >= target_samples:
                all_samples = np.hstack(samples_buffer)
                self.data_queue.put(all_samples)  # ส่งข้อมูลไปที่คิว
                print("สะสมครบ 1000 ตัวอย่างแล้ว ส่งข้อมูลไปที่คิว")
                total_samples_collected = 0  # รีเซ็ตตัวแปรเพื่อสะสมตัวอย่างใหม่
                samples_buffer = []  # เคลียร์บัฟเฟอร์
                self.ready_for_processing = True  # ตั้งสถานะเป็นพร้อมที่จะนำข้อมูลไปประมวลผล
                self.running = False
                sleep(0.1)  # รอเพื่อให้โปรแกรมหลักส่งสัญญาณให้เริ่มการสะสมข้อมูลใหม่
            else:
                sleep(0.1)  # รอสักครู่ก่อนที่จะวนลูปการรับข้อมูลใหม่

    def process_data(self):
        while True:
            if self.ready_for_processing and not self.data_queue.empty():
                data = self.data_queue.get()
                # ประมวลผลข้อมูลที่นี่
                print(f"กำลังประมวลผลข้อมูลขนาด: {data.shape}")
                self.ready_for_processing = False  # ตั้งสถานะเป็นไม่พร้อมสำหรับการประมวลผลใหม่
            else:
                sleep(0.1)

# สร้างอินสแตนซ์ของ EEGReceiver
receiver = EEGReceiver()

# เริ่มเธรดการรับข้อมูล
eeg_thread = threading.Thread(target=receiver.receive_eeg_data, daemon=True)
eeg_thread.start()

# เริ่มเธรดการประมวลผลข้อมูล
processing_thread = threading.Thread(target=receiver.process_data, daemon=True)
processing_thread.start()


receiver.running = True
    