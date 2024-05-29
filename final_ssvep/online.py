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
      # self.refresh_rate = self.mywin.getActualFrameRate()
      # print(refresh_rate)

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
        c = 0
        while True:
            Trialclock = core.Clock()
            self.text.setAutoDraw(True)
            self.mywin.flip()
            while True:
                if Trialclock.getTime() >= 5:
                    break
            self.text.setAutoDraw(False)
            self.mywin.flip()
            state = []
            indices = np.arange(0,60*10) # 60 => 1 sec / 10 sec``
            fre_fix1 = self.frequency_cal(2,144,indices)
            fre_fix2 = self.frequency_cal(4,144,indices)
            fre_fix3 = self.frequency_cal(5,144,indices)
            fre_fix4 = self.frequency_cal(6,144,indices)

            fre_fix = [fre_fix1, fre_fix2, fre_fix3, fre_fix4]
            self.fixation.setAutoDraw(True)
            for i in range(len(indices)):
                state = []
                for j in range(len(fre_fix)):
                    if fre_fix[j][i] == 1:
                        state.append(True)
                    elif fre_fix[j][i] == 0:
                        state.append(False)
                self.pattern1.setAutoDraw(True)
                self.pattern3.setAutoDraw(True)
                self.pattern5.setAutoDraw(True)
                self.pattern7.setAutoDraw(True)
                self.mywin.flip()
                self.pattern1.setAutoDraw(state[0])
                self.pattern2.setAutoDraw(not state[0])
                self.pattern3.setAutoDraw(state[1])
                self.pattern4.setAutoDraw(not state[1])
                self.pattern5.setAutoDraw(state[2])
                self.pattern6.setAutoDraw(not state[2])
                self.pattern7.setAutoDraw(state[3])
                self.pattern8.setAutoDraw(not state[3])
    
            Trialclock = core.Clock()
            self.text_trial.setAutoDraw(True)
            self.fixation.setAutoDraw(False)     
            self.pattern1.setAutoDraw(False)
            self.pattern2.setAutoDraw(False)
            self.pattern3.setAutoDraw(False)
            self.pattern4.setAutoDraw(False)
            self.pattern5.setAutoDraw(False)
            self.pattern6.setAutoDraw(False)
            self.pattern7.setAutoDraw(False)
            self.pattern8.setAutoDraw(False)
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
            self.pattern3.setAutoDraw(False)
            self.pattern4.setAutoDraw(False)
            self.pattern5.setAutoDraw(False)
            self.pattern6.setAutoDraw(False)
            self.pattern7.setAutoDraw(False)
            self.pattern8.setAutoDraw(False)
            self.mywin.flip()
            if c == num_trial:
                break
        self.stop()

stimuli=SSVEP()
stimuli.start()

   
      

                
                
      