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
import socket

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

class SSVEP(object):
    def __init__(self, mywin=visual.Window([1600, 800], fullscr=False, monitor='testMonitor', units='deg')):
        self.mywin = mywin
        self.pattern1 = visual.GratingStim(win=self.mywin, name='pattern1', units='cm',
                                           tex=None, mask=None,
                                           ori=0, pos=[11, 0], size=20, sf=1, phase=0.0,
                                           color=[1,1,1], colorSpace='rgb', opacity=1,
                                           texRes=256, interpolate=True, depth=-1.0)
        self.pattern2 = visual.GratingStim(win=self.mywin, name='pattern2', units='cm',
                                           tex=None, mask=None,
                                           ori=0, pos=[11, 0], size=20, sf=1, phase=0,
                                           color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                                           texRes=256, interpolate=True, depth=-2.0)
        
        self.pattern3 = visual.GratingStim(win=self.mywin, name='pattern3', units='cm',
                                           tex=None, mask=None,
                                           ori=0, pos=[-11, 0], size=20, sf=1, phase=0.0,
                                           color=[1,1,1], colorSpace='rgb', opacity=1,
                                           texRes=256, interpolate=True, depth=-1.0)
        self.pattern4 = visual.GratingStim(win=self.mywin, name='pattern4', units='cm',
                                           tex=None, mask=None,
                                           ori=0, pos=[-11, 0], size=20, sf=1, phase=0,
                                           color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                                           texRes=256, interpolate=True, depth=-2.0)
        
        self.pattern5 = visual.GratingStim(win=self.mywin, name='pattern5', units='cm',
                                           tex=None, mask=None,
                                           ori=0, pos=[-6, 6], size=10, sf=1, phase=0.0,
                                           color=[1,1,1], colorSpace='rgb', opacity=1,
                                           texRes=256, interpolate=True, depth=-1.0)
        self.pattern6 = visual.GratingStim(win=self.mywin, name='pattern6', units='cm',
                                           tex=None, mask=None,
                                           ori=0, pos=[-6, 6], size=10, sf=1, phase=0,
                                           color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                                           texRes=256, interpolate=True, depth=-2.0)
        
        self.pattern7 = visual.GratingStim(win=self.mywin, name='pattern7', units='cm',
                                           tex=None, mask=None,
                                           ori=0, pos=[6, -6], size=10, sf=1, phase=0.0,
                                           color=[1,1,1], colorSpace='rgb', opacity=1,
                                           texRes=256, interpolate=True, depth=-1.0)
        self.pattern8 = visual.GratingStim(win=self.mywin, name='pattern8', units='cm',
                                           tex=None, mask=None,
                                           ori=0, pos=[6, -6], size=10, sf=1, phase=0,
                                           color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                                           texRes=256, interpolate=True, depth=-2.0)
        
        self.fixation = visual.GratingStim(win=self.mywin, size=0.3, pos=[0,0], sf=0, rgb=-1)
        self.refresh_rate = self.mywin.getActualFrameRate()
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
    
    def frequency_cal(self, frequency, refresh_rate, indices):
        ans = signal.square(2*np.pi*frequency*(indices/refresh_rate))
        ans = (ans+1)/2
        return ans
    
    def stop(self):
        self.mywin.close()
        core.quit()

    def start(self):
        num_trial = 5
        c = 0
        block_dur = 6
        while self.refresh_rate is None:
            self.refresh_rate = self.mywin.getActualFrameRate()
            pass
        print(self.refresh_rate)
        try:
            while True:
                Trialclock = core.Clock()
                self.text.setAutoDraw(True)
                self.mywin.flip()
                while True:
                    if Trialclock.getTime() >= 5:
                        break
                self.text.setAutoDraw(False)
                self.mywin.flip()
                i = 0
                ratio = 1
                indices = np.arange(0,self.refresh_rate/ratio)
                fre_fix1 = self.frequency_cal(6,self.refresh_rate/ratio,indices)
                fre_fix2 = self.frequency_cal(20,self.refresh_rate/ratio,indices)

                fre_fix = [fre_fix1, fre_fix2]
                t_start = core.Clock()
                fre1 = []
                fre2 = []

                # ส่งข้อมูลไปยัง server
                message = "receiver.running = True"
                try:
                    client_socket.send(message.encode('utf-8'))
                except Exception as e:
                    print(f"Failed to send message to server: {e}")

                while t_start.getTime() <= block_dur:
                    state = []
                    for j in range(len(fre_fix)):
                        if fre_fix[j][i % len(indices)] == 1:
                            state.append(True)
                        elif fre_fix[j][i % len(indices)] == 0:
                            state.append(False)
                    self.pattern1.setAutoDraw(True)
                    self.pattern3.setAutoDraw(True)
                    self.mywin.flip()
                    self.pattern1.setAutoDraw(state[0])
                    self.pattern2.setAutoDraw(not state[0])
                    self.pattern3.setAutoDraw(state[1])
                    self.pattern4.setAutoDraw(not state[1])
                    fre1.append([fre_fix1[i % len(indices)],datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')])
                    fre2.append([fre_fix2[i % len(indices)],datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')])
                    i += 1

                Trialclock = core.Clock()
                self.text_trial.setAutoDraw(True)
                self.pattern1.setAutoDraw(False)
                self.pattern2.setAutoDraw(False)
                self.pattern3.setAutoDraw(False)
                self.pattern4.setAutoDraw(False)
                frequency1 = calculate_frequency(fre1)
                frequency2 = calculate_frequency(fre2)
                print(f'Frequency1 = {frequency1} Hz')
                print(f'Frequency2 = {frequency2} Hz')
                print(f'END time {t_start.getTime()}')
                print(f'END trail {c + 1}')

                self.mywin.flip()
                while True:
                    if Trialclock.getTime() >= 5:
                        break
                self.text_trial.setAutoDraw(False)
                self.pattern1.setAutoDraw(False)
                self.pattern2.setAutoDraw(False)
                self.pattern3.setAutoDraw(False)
                self.pattern4.setAutoDraw(False)
                self.mywin.flip()
                c += 1
                if c == num_trial:
                    break
        finally:
            client_socket.close()
            self.stop()

# ตั้งค่าที่อยู่ IP และพอร์ตของ server
server_ip = '192.168.1.110'  # แทนที่ด้วย IP ของเครื่อง server
server_port = 6000

# สร้าง socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# เชื่อมต่อกับ server
try:
    client_socket.connect((server_ip, server_port))
except Exception as e:
    print(f"Failed to connect to server: {e}")
    client_socket.close()
    exit(1)

stimuli = SSVEP()
stimuli.start()
