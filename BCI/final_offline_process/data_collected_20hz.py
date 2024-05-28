from psychopy import visual, core, event, gui
import numpy as np
import scipy.signal as signal
from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_stream
import pyxdf
import mne
import pandas as pd
from mne.decoding import CSP
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC 
from sklearn.metrics import classification_report
from sklearn.svm import SVC 
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from datetime import datetime
import csv
from datetime import datetime, timedelta
import os

def calculate_frequency(signal,name):
    # Calculate the total frequency
    signal_changes = 0
    previous_signal = None
    
    for i in range(1, len(signal)):
        current_signal, current_time = signal[i]
        previous_signal, previous_time = signal[i-1]
        if previous_signal is not None:
            if previous_signal == 1 and current_signal == 0:
                signal_changes += 1
    
    start_time = datetime.strptime(signal[0][1], '%Y-%m-%d %H:%M:%S.%f')
    end_time = datetime.strptime(signal[-1][1], '%Y-%m-%d %H:%M:%S.%f')
    total_duration = (end_time - start_time).total_seconds()
    total_frequency = signal_changes / total_duration if total_duration > 0 else 0
    
    # Calculate frequency per second and append to CSV
    per_second_changes = {}
    for i in range(1, len(signal)):
        current_signal, current_time = signal[i]
        previous_signal, previous_time = signal[i-1]
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S.%f')
        previous_time = datetime.strptime(previous_time, '%Y-%m-%d %H:%M:%S.%f')
        if previous_signal == 1 and current_signal == 0:
            second = current_time.replace(microsecond=0)
            if second not in per_second_changes:
                per_second_changes[second] = 0
            per_second_changes[second] += 1
    
    file_exists = os.path.isfile('frequency_per_second.csv')
    with open('frequency_per_second.csv', 'a', newline='') as csvfile:
        fieldnames = ['Time', 'Frequency']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write the header only if the file does not exist
        if not file_exists:
            writer.writeheader()
        
        current_time = start_time.replace(microsecond=0)
        while current_time <= end_time:
            frequency = per_second_changes.get(current_time, 0)
            writer.writerow({'Time': current_time.strftime('%Y-%m-%d %H:%M:%S'), 'Frequency': f"{frequency:.2f}"})
            current_time += timedelta(seconds=1)
    
    return round(total_frequency, 2)

class SSVEP(object):
   def __init__(self, mywin= visual.Window([800, 800], fullscr=False, monitor='testMonitor',units='deg', pos=(900,150))):

      self.mywin = mywin
      self.pattern1 = visual.GratingStim(win=self.mywin, name='pattern1',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=20, sf=1, phase=0.0,
                        color=[1,1,1], colorSpace='rgb', opacity=1, 
                        texRes=256, interpolate=True, depth=-1.0)
      self.pattern2 = visual.GratingStim(win=self.mywin, name='pattern2',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=20, sf=1, phase=0,
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
      print(self.refresh_rate)

      self.text = visual.TextStim(win=self.mywin, name='text',
                        text='Ready and Prepare \nfor the Offline session',
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
        num_trial = 10
        c = 0
        block_dur = 6
        while self.refresh_rate is None:
                self.refresh_rate = self.mywin.getActualFrameRate()
                pass
        # self.refresh_rate = 120
        print(self.refresh_rate)
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
            f = 20
            indices = np.arange(0,self.refresh_rate/ratio) 
            fre_fix1 = self.frequency_cal(f,self.refresh_rate/ratio,indices)

            fre_fix = [fre_fix1]
            self.fixation.setAutoDraw(True)
            t_start = core.Clock()
            fre = []
            while t_start.getTime() <= block_dur:
                state = []
                for j in range(len(fre_fix)):
                    if fre_fix[j][i % len(indices)] == 1:
                        state.append(True)
                    elif fre_fix[j][i % len(indices)] == 0:
                        state.append(False)
                self.pattern1.setAutoDraw(True)
                self.mywin.flip()
                self.pattern1.setAutoDraw(state[0])
                self.pattern2.setAutoDraw(not state[0])
                fre.append([fre_fix1[i % len(indices)],datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')])
                i += 1

            Trialclock = core.Clock()
            self.text_trial.setAutoDraw(True)
            self.fixation.setAutoDraw(False)     
            self.pattern1.setAutoDraw(False)
            self.pattern2.setAutoDraw(False)
            frequency1 = calculate_frequency(fre,f'{f}')
            print(f'Frequency1 = {frequency1}')
            print(f'END time {t_start.getTime()}')
            print(f'END trail {c + 1}')

            self.mywin.flip()
            while True:
                if Trialclock.getTime() >= 5:
                    break
            self.text_trial.setAutoDraw(False)
            self.fixation.setAutoDraw(False) 
      
            c += 1
            self.fixation.setAutoDraw(False)     
            self.pattern1.setAutoDraw(False)
            self.pattern2.setAutoDraw(False)
            self.mywin.flip()
            if c == num_trial:
                break
        self.stop()

stimuli=SSVEP()
stimuli.start()

   
      

                
                
      