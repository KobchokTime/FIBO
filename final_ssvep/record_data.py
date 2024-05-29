from InputBox import InputBox
from psychopy import visual, core, event, gui
import numpy as np
import scipy.signal as signal
from pylsl import StreamInfo, StreamOutlet

class SSVEP(object):
   def __init__(self, mywin= visual.Window([1200, 800], fullscr=False, monitor='testMonitor',units='deg')):
      
      info = StreamInfo(name='marker_stream', type='Markers', channel_count=1,
      channel_format='int32', source_id='myuniqueid1234')
      self.outlet = StreamOutlet(info) 
      self.mywin = mywin

    #   self.myDlg = gui.Dlg(title="OpenBCI Menu")
    # #   self.myDlg.addText('Subject info')
    # #   self.myDlg.addField('Participant:')#0
    # #   self.myDlg.addField('Session', 1)#1
    #   self.myDlg.show()  # show dialog and wait for OK or Cancel
    #   if self.myDlg.OK:  # then the user pressed OK
    #       self.thisInfo = self.myDlg.data
    #   else:
    #       print('User Cancelled')

      self.fixation = visual.GratingStim(win=self.mywin, size = 0.3, pos=[0,0], sf=0, rgb=-1)
      
      
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
                        ori=0, pos=[0, 0], size=20, sf=1, phase=0.0,
                        color=[1,1,1], colorSpace='rgb', opacity=1, 
                        texRes=256, interpolate=True, depth=-1.0)
      self.pattern4 = visual.GratingStim(win=self.mywin, name='pattern4',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=20, sf=1, phase=0,
                        color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                        texRes=256, interpolate=True, depth=-2.0)
      
      self.pattern5 = visual.GratingStim(win=self.mywin, name='pattern5',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=20, sf=1, phase=0.0,
                        color=[1,1,1], colorSpace='rgb', opacity=1, 
                        texRes=256, interpolate=True, depth=-1.0)
      self.pattern6 = visual.GratingStim(win=self.mywin, name='pattern6',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=20, sf=1, phase=0,
                        color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                        texRes=256, interpolate=True, depth=-2.0)
      
      self.pattern7 = visual.GratingStim(win=self.mywin, name='pattern7',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=20, sf=1, phase=0.0,
                        color=[1,1,1], colorSpace='rgb', opacity=1, 
                        texRes=256, interpolate=True, depth=-1.0)
      self.pattern8 = visual.GratingStim(win=self.mywin, name='pattern8',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=20, sf=1, phase=0,
                        color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                        texRes=256, interpolate=True, depth=-2.0)
      
      self.text = visual.TextStim(win=self.mywin, name='text',
                        text='Ready and Prepare \nfor the experiment',
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
      self.refresh_rate = self.mywin.getActualFrameRate()
      print(self.refresh_rate)
      
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
        self.outlet.push_sample([0])
        while True:
            Trialclock = core.Clock()
            self.text.setAutoDraw(True)
            self.mywin.flip()
            while True:
                if Trialclock.getTime() >= 5:
                    break
            self.text.setAutoDraw(False)
            
            indices = np.arange(0,self.refresh_rate) 
            fre_fix1 = self.frequency_cal(7,self.refresh_rate,indices)
            fre_fix2 = self.frequency_cal(9,self.refresh_rate,indices)
            fre_fix3 = self.frequency_cal(11,self.refresh_rate,indices)
            fre_fix4 = self.frequency_cal(13,self.refresh_rate,indices)
            self.fixation.setAutoDraw(True)
            
            self.outlet.push_sample([1])
            t_start = core.Clock()
            for i in range(len(indices)):
                # print(f'1 {i}')
                self.fixation.setAutoDraw(True)
                self.pattern1.setAutoDraw(True)
                self.mywin.flip()
                if fre_fix1[i] == 1:
                    self.mywin.flip()
                    self.pattern1.setAutoDraw(False)
                    self.pattern2.setAutoDraw(True)
                elif fre_fix1[i] == 0:
                    self.mywin.flip()
                    self.pattern2.setAutoDraw(False)
            print(f'END time {t_start.getTime()}')
            print(f'END trail {count_trial} in 7.5 Hz ')
            self.fixation.setAutoDraw(False)     
            self.pattern1.setAutoDraw(False)
            self.pattern2.setAutoDraw(False)

            Trialclock = core.Clock()
            self.text_break.setAutoDraw(True)
            self.mywin.flip()
            self.outlet.push_sample([0])
            while True:
                if Trialclock.getTime() >= 5:
                    break
            self.text_break.setAutoDraw(False)
            self.fixation.setAutoDraw(True)   

            self.outlet.push_sample([2])
            for i in range(len(indices)):
                # print(f'2 {i}')
                self.fixation.setAutoDraw(True)
                self.pattern3.setAutoDraw(True)
                self.mywin.flip()
                if fre_fix2[i] == 1:
                    self.mywin.flip()
                    self.pattern3.setAutoDraw(False)
                    self.pattern4.setAutoDraw(True)
                elif fre_fix2[i] == 0:
                    self.mywin.flip()
                    self.pattern4.setAutoDraw(False)

            self.fixation.setAutoDraw(False)     
            self.pattern3.setAutoDraw(False)
            self.pattern4.setAutoDraw(False)
            print(f'END trail {count_trial} in 12 Hz ')

            Trialclock = core.Clock()
            self.text_break.setAutoDraw(True)
            self.mywin.flip()
            self.outlet.push_sample([0])
            while True:
                if Trialclock.getTime() >= 5:
                    break
            self.text_break.setAutoDraw(False)
            self.fixation.setAutoDraw(True) 

            self.outlet.push_sample([3])
            for i in range(len(indices)):
                # print(f'3 {i}')
                self.fixation.setAutoDraw(True)
                self.pattern5.setAutoDraw(True)
                self.mywin.flip()
                if fre_fix3[i] == 1:
                    self.mywin.flip()
                    self.pattern5.setAutoDraw(False)
                    self.pattern6.setAutoDraw(True)
                elif fre_fix3[i] == 0:
                    self.mywin.flip()
                    self.pattern6.setAutoDraw(False)

            self.fixation.setAutoDraw(False)     
            self.pattern5.setAutoDraw(False)
            self.pattern6.setAutoDraw(False)
            print(f'END trail {count_trial} in 20 Hz ')

            Trialclock = core.Clock()
            self.text_break.setAutoDraw(True)
            self.mywin.flip()
            self.outlet.push_sample([0])
            while True:
                if Trialclock.getTime() >= 5:
                    break
            self.text_break.setAutoDraw(False)
            self.fixation.setAutoDraw(True) 

            self.outlet.push_sample([4])
            for i in range(len(indices)):
                # print(f'4 {i}')
                self.fixation.setAutoDraw(True)
                self.pattern7.setAutoDraw(True)
                self.mywin.flip()
                if fre_fix4[i] == 1:
                    self.mywin.flip()
                    self.pattern7.setAutoDraw(False)
                    self.pattern8.setAutoDraw(True)
                elif fre_fix4[i] == 0:
                    self.mywin.flip()
                    self.pattern8.setAutoDraw(False)

            self.fixation.setAutoDraw(False)     
            self.pattern7.setAutoDraw(False)
            self.pattern8.setAutoDraw(False)
            print(f'END trail {count_trial} in 35 Hz ')
            Trialclock = core.Clock()
            self.text_trial.setAutoDraw(True)
            self.mywin.flip()
            self.outlet.push_sample([0])
            while True:
                if Trialclock.getTime() >= 5:
                    break
            self.text_trial.setAutoDraw(False)
            self.fixation.setAutoDraw(False) 
            count_trial += 1
            if count_trial == num_trial:
                break
        self.text_end.setAutoDraw(True)
        self.mywin.flip()
        self.outlet.push_sample([0])
        while True:
            if Trialclock.getTime() >= 5:
                break
        self.text_end.setAutoDraw(False)
        self.stop()

stimuli=SSVEP()
stimuli.start()