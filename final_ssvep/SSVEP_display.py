from InputBox import InputBox
from psychopy import visual, core, event, gui
import numpy as np
import scipy.signal as signal
from pylsl import StreamInfo, StreamOutlet


class SSVEP(object):
   def __init__(self, mywin= visual.Window([1200, 800], fullscr=False, monitor='testMonitor',units='deg')):
      
      # self.myDlg = gui.Dlg(title="OpenBCI Menu")
      # self.myDlg.addText('Subject info')
      # self.myDlg.addField('Participant:')#0
      # self.myDlg.addField('Session', 1)#1
      # self.myDlg.show()  # show dialog and wait for OK or Cancel
      # if self.myDlg.OK:  # then the user pressed OK
      #    self.thisInfo = self.myDlg.data
      #    self.options = {'participant': self.thisInfo[0], 'session': self.thisInfo[1]}
      # else:
      #    print('User Cancelled')

      #       # Setup filename for saving
      # self.fname = '%s_%s.csv' %(self.options['participant'], self.options['session'])

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
      
   def frequency_cal(self,frequency, refresh_rate, indices):
      ans = signal.square(2*np.pi*frequency*(indices/refresh_rate))
      ans = (ans+1)/2
      return ans
   
   def stop(self):
        self.mywin.close()
        core.quit()

   def start(self):
      #   info = StreamInfo(name='marker_stream', type='Markers', channel_count=1,
      #   channel_format='int32', source_id='myuniqueid1234')
      #   outlet = StreamOutlet(info) 
        state = []
        indices = np.arange(0,60*5) # 60 => 1 sec
        fre_fix1 = self.frequency_cal(7.5,144,indices)
        fre_fix2 = self.frequency_cal(12,144,indices)
        fre_fix3 = self.frequency_cal(20,144,indices)
        fre_fix4 = self.frequency_cal(35,144,indices)

        fre_fix = [fre_fix1, fre_fix2, fre_fix3, fre_fix4]
        self.fixation.setAutoDraw(True)
        for i in range(len(indices)):
         state = []
         for j in range(len(fre_fix)):
             if fre_fix[j][i] == 1:
                 state.append(True)
             elif fre_fix[j][i] == 0:
                 state.append(False)
         # outlet.push_sample([1])
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

        self.stop()

stimuli=SSVEP()
stimuli.start()

   
      

                
                
      