import threading
import time 
from pylsl import resolve_stream, StreamInlet, StreamInfo, StreamOutlet
from queue import Queue
from scipy.signal import welch
from joblib import load
from psychopy import visual, core, event, gui
import numpy as np
import scipy.signal as signal
import csv
from datetime import datetime

def calculate_frequency(signal):
    # Count the number of signal changes
    signal_changes = 0
    previous_signal = None
    
    # Iterate over the signal list
    for i in range(1, len(signal)):
        current_signal, current_time = signal[i]
        previous_signal, previous_time = signal[i-1]
        if previous_signal is not None:
            if previous_signal == 1 and current_signal == 0:
                signal_changes += 1
    
    # Calculate the total time duration
    start_time = datetime.strptime(signal[0][1], '%Y-%m-%d %H:%M:%S.%f')
    end_time = datetime.strptime(signal[-1][1], '%Y-%m-%d %H:%M:%S.%f')
    total_duration = (end_time - start_time).total_seconds()
    
    # Calculate frequency
    frequency = signal_changes / total_duration
    
    return frequency

class EEGReceiver:
    def __init__(self):
        self.data_queue = Queue()
        self.running = False
        self.ready_for_processing = False
        self.start_time = None  # เพิ่มตัวแปรเพื่อเก็บเวลาเริ่มต้น

    def receive_eeg_data(self):
        target_duration = 4  # 4 วินาที
        num_samples_per_iteration = 250  
        target_stream_name = 'obci_eeg1'
        
        print("Searching for streams...")
        All_streams = resolve_stream()
        EEG_streams = [stream for stream in All_streams if stream.name() == target_stream_name]
        
        if len(EEG_streams) == 0:
            print("Error: No EEG stream found.")
            return
        
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
                    self.start_time = time.time()  # เก็บเวลาเริ่มต้น
                
                samples = []
                for i in range(num_samples_per_iteration):
                    sample, timestamp = inlet.pull_sample()
                    if sample is not None:
                        samples.append(sample)
                
                if samples:
                    samples_buffer.append(np.array(samples).T)
                    total_samples_collected += len(samples)
                    # print(f"Get {len(samples)} samples, buffer size: {total_samples_collected}")
         
                current_time = time.time()
                if current_time - self.start_time >= target_duration:
                    all_samples = np.hstack(samples_buffer)
                    self.data_queue.put(all_samples) 
                    print("4 seconds have passed Send information to the queue")
                    total_samples_collected = 0 
                    samples_buffer = []  
                    self.ready_for_processing = True 
                    state = 0
                    self.running = False
                    self.start_time = None  # reset เวลาเริ่มต้น
                 

    def process_data(self):
        rf_model = load('./model_FFT/best_rf_classifier.joblib')
        svm_model = load('./model_FFT/best_svm_classifier.joblib')
        lda_model = load('./model_FFT/best_lda_classifier.joblib')
        knn_model = load('./model_FFT/best_knn_classifier.joblib')
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
                # print(f"Processing data size: {combined.shape}")
                pre_rf = rf_model.predict(combined)
                pre_svm = svm_model.predict(combined)
                pre_lda = lda_model.predict(combined)
                pre_knn = knn_model.predict(combined)

                print(f'pre_rf => {pre_rf}')
                print(f'pre_svm => {pre_svm}')
                print(f'pre_lda => {pre_lda}')
                print(f'pre_knn => {pre_knn}')
                
                
                self.ready_for_processing = False  
        
receiver = EEGReceiver()

eeg_thread = threading.Thread(target=receiver.receive_eeg_data, daemon=True)
eeg_thread.start()

processing_thread = threading.Thread(target=receiver.process_data, daemon=True)
processing_thread.start()

# receiver.running = True
class SSVEP(object):
   def __init__(self, mywin= visual.Window([1200, 800], fullscr=False, monitor='testMonitor',units='deg')):
      self.mywin = mywin
      self.pattern1 = visual.GratingStim(win=self.mywin, name='pattern1',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[6, 6], size=10, sf=1, phase=0.0,
                        color=[1,1,1], colorSpace='rgb', opacity=1, 
                        texRes=256, interpolate=True, depth=-1.0)
      self.pattern2 = visual.GratingStim(win=self.mywin, name='pattern2',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[6, 6], size=10, sf=1, phase=0,
                        color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                        texRes=256, interpolate=True, depth=-2.0)
      
      self.pattern3 = visual.GratingStim(win=self.mywin, name='pattern3',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[-6, -6], size=10, sf=1, phase=0.0,
                        color=[1,1,1], colorSpace='rgb', opacity=1, 
                        texRes=256, interpolate=True, depth=-1.0)
      self.pattern4 = visual.GratingStim(win=self.mywin, name='pattern4',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[-6, -6], size=10, sf=1, phase=0,
                        color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                        texRes=256, interpolate=True, depth=-2.0)
      
      self.pattern5 = visual.GratingStim(win=self.mywin, name='pattern5',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[-6, 6], size=10, sf=1, phase=0.0,
                        color=[1,1,1], colorSpace='rgb', opacity=1, 
                        texRes=256, interpolate=True, depth=-1.0)
      self.pattern6 = visual.GratingStim(win=self.mywin, name='pattern6',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[-6, 6], size=10, sf=1, phase=0,
                        color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                        texRes=256, interpolate=True, depth=-2.0)
      
      self.pattern7 = visual.GratingStim(win=self.mywin, name='pattern7',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[6, -6], size=10, sf=1, phase=0.0,
                        color=[1,1,1], colorSpace='rgb', opacity=1, 
                        texRes=256, interpolate=True, depth=-1.0)
      self.pattern8 = visual.GratingStim(win=self.mywin, name='pattern8',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[6, -6], size=10, sf=1, phase=0,
                        color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                        texRes=256, interpolate=True, depth=-2.0)
      
      self.fixation = visual.GratingStim(win=self.mywin, size = 0.3, pos=[0,0], sf=0, rgb=-1)
      self.refresh_rate = self.mywin.getActualFrameRate()
    #   print(refresh_rate)

      self.text = visual.TextStim(win=self.mywin, name='text',
                        text='Ready and Prepare \nfor the Online experiment test result',
                        font='Open Sans',
                        pos=(0, 0), height=1, wrapWidth=None, ori=0.0, 
                        color='Black', colorSpace='rgb', opacity=None, 
                        languageStyle='LTR',
                        depth=0.0)
      
      self.text_break = visual.TextStim(win=self.mywin, name='text_break',
                        text='Please take a short break 5 sec',
                        font='Open Sans',
                        pos=(0, 0), height=1, wrapWidth=None, ori=0.0, 
                        color='Black', colorSpace='rgb', opacity=None, 
                        languageStyle='LTR',
                        depth=0.0)
      self.text_end = visual.TextStim(win=self.mywin, name='text_end',
                        text='Thank you',
                        font='Open Sans',
                        pos=(0, 0), height=1, wrapWidth=None, ori=0.0, 
                        color='Black', colorSpace='rgb', opacity=None, 
                        languageStyle='LTR',
                        depth=0.0)
      self.text_trial = visual.TextStim(win=self.mywin, name='text_trial',
                        text='Please take a short break 10 sec before next Trial',
                        font='Open Sans',
                        pos=(0, 0), height=1, wrapWidth=None, ori=0.0, 
                        color='Black', colorSpace='rgb', opacity=None, 
                        languageStyle='LTR',
                        depth=0.0)
      
   def frequency_cal(self,frequency, refresh_rate, indices):
      ans = signal.square(2*np.pi*frequency*(indices/refresh_rate))
      ans = (ans+1)/2
      return ans
   
   def stop(self):
        self.mywin.close()
        core.quit()

   def start(self):
        num_trial = 5
        count_trial = 0
        block_dur = 5
        fre1 = 6
        fre2 = 20
        ratio = 1
        while True:
            state = []
            signal1 = []
            signal2 = []
            # while self.refresh_rate is None:
            #     self.refresh_rate = self.mywin.getActualFrameRate()
            #     pass
            self.refresh_rate = 144
            print(self.refresh_rate)
            Trialclock = core.Clock()
            self.text.setAutoDraw(True)
            self.mywin.flip()
            while True:
                if Trialclock.getTime() >= 5:
                    break
            self.text.setAutoDraw(False)
            indices = np.arange(0,self.refresh_rate/ratio) 
            fre_fix1 = self.frequency_cal(fre1,self.refresh_rate/ratio,indices)
            fre_fix2 = self.frequency_cal(fre2,self.refresh_rate/ratio,indices)
            fre_fix1 = [bool(int(x)) for x in fre_fix1]
            fre_fix2 = [bool(int(x)) for x in fre_fix2]
            for i in range(len(indices)):
                state.append([fre_fix1[i],fre_fix2[i]])
            t_start = core.Clock()
            i = 0
            receiver.running = True
            while t_start.getTime() <= block_dur:
                self.pattern1.setAutoDraw(True)
                self.pattern3.setAutoDraw(True)
                self.mywin.flip()
                self.pattern1.setAutoDraw(state[i % len(state)][0])
                self.pattern2.setAutoDraw(not state[i % len(state)][0])
                self.pattern3.setAutoDraw(state[i % len(state)][1])
                self.pattern4.setAutoDraw(not state[i % len(state)][1])
                signal1.append([fre_fix1[i % len(state)],datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')])
                signal2.append([fre_fix2[i % len(state)],datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')])
                i += 1  
            frequency1 = calculate_frequency(signal1)
            frequency2 = calculate_frequency(signal2)
            print(f'Frequency1 = {frequency1}')
            print(f'Frequency2 = {frequency2}')
            print(f'END time {t_start.getTime()}')
            print(f'END trail {count_trial + 1}')
            self.pattern1.setAutoDraw(False)
            self.pattern2.setAutoDraw(False)
            self.pattern3.setAutoDraw(False)
            self.pattern4.setAutoDraw(False)

            Trialclock = core.Clock()
            self.text_break.setAutoDraw(True)
            self.mywin.flip()
            while True:
                if Trialclock.getTime() >= 5:
                    break
            self.text_break.setAutoDraw(False)
            count_trial += 1
            if count_trial == num_trial:
                break

stimuli=SSVEP()
stimuli.start()