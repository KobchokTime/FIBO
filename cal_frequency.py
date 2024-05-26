from InputBox import InputBox
from psychopy import visual, core, event, gui
import numpy as np
import scipy.signal as signal
from pylsl import StreamInfo, StreamOutlet
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

def save_to_csv(filename, signal):
    """
    Save current time (with milliseconds) and signal values to a CSV file.
    
    Parameters:
        filename (str): The name of the CSV file.
        signal (float): The signal value to be saved.
    """
    # Get current time with milliseconds
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    
    # Check if the file exists
    file_exists = False
    try:
        with open(filename, 'r') as file:
            file_exists = True
    except FileNotFoundError:
        pass
    
    # Open the CSV file in append mode
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        
        # Write header if file is newly created
        if not file_exists:
            writer.writerow(['Time', 'Signal'])  # Set column names
        
        # Write data to the file
        writer.writerow([current_time, signal])
    
    # print(f"Data (Time: {current_time}, Signal: {signal}) saved to {filename}")
class SSVEP(object):
   def __init__(self, mywin= visual.Window([1920,1080 ], fullscr = False, monitor='testMonitor',units='deg')):
      
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
                        ori=0, pos=[0, 0], size=30, sf=1, phase=0.0,
                        color=[1,1,1], colorSpace='rgb', opacity=1, 
                        texRes=256, interpolate=True, depth=-1.0)
      self.pattern2 = visual.GratingStim(win=self.mywin, name='pattern2',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=30, sf=1, phase=0,
                        color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                        texRes=256, interpolate=True, depth=-2.0)
      
      self.pattern3 = visual.GratingStim(win=self.mywin, name='pattern3',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=30, sf=1, phase=0.0,
                        color=[1,1,1], colorSpace='rgb', opacity=1, 
                        texRes=256, interpolate=True, depth=-1.0)
      self.pattern4 = visual.GratingStim(win=self.mywin, name='pattern4',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=30, sf=1, phase=0,
                        color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                        texRes=256, interpolate=True, depth=-2.0)
      
      self.pattern5 = visual.GratingStim(win=self.mywin, name='pattern5',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=30, sf=1, phase=0.0,
                        color=[1,1,1], colorSpace='rgb', opacity=1, 
                        texRes=256, interpolate=True, depth=-1.0)
      self.pattern6 = visual.GratingStim(win=self.mywin, name='pattern6',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=30, sf=1, phase=0,
                        color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                        texRes=256, interpolate=True, depth=-2.0)
      
      self.pattern7 = visual.GratingStim(win=self.mywin, name='pattern7',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=30, sf=1, phase=0.0,
                        color=[1,1,1], colorSpace='rgb', opacity=1, 
                        texRes=256, interpolate=True, depth=-1.0)
      self.pattern8 = visual.GratingStim(win=self.mywin, name='pattern8',units='cm', 
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=30, sf=1, phase=0,
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
        # ##self.outlet.push_sample([0])
        block_dur = 4
        fre1 = 6
        # fre2 = 7
        # fre3 = 7
        # fre4 = 7
        ratio = 6/2.5
        # ratio = 6
        
        while True:
            # self.refresh_rate = self.mywin.getActualFrameRate()
            # self.outlet.push_sample([0])
            while self.refresh_rate is None:
                self.refresh_rate = self.mywin.getActualFrameRate()
                pass
            print(self.refresh_rate)
            Trialclock = core.Clock()
            self.text.setAutoDraw(True)
            self.mywin.flip()
            while True:
                if Trialclock.getTime() >= 1:
                    break
            self.text.setAutoDraw(False)
            
            indices = np.arange(0,self.refresh_rate/ratio) 
            fre_fix1 = self.frequency_cal(fre1,self.refresh_rate/ratio,indices)
            # fre_fix2 = self.frequency_cal(fre2,self.refresh_rate/ratio,indices)
            # fre_fix3 = self.frequency_cal(fre3,self.refresh_rate/ratio,indices)
            # fre_fix4 = self.frequency_cal(fre4,self.refresh_rate/ratio,indices)
            self.fixation.setAutoDraw(True)
            
            #self.outlet.push_sample
            t_start = core.Clock()
            i = 0
            signal = []
            while t_start.getTime() <= block_dur:
                # print(f'1 {i}')
                self.fixation.setAutoDraw(True)
                self.pattern1.setAutoDraw(True)
                self.mywin.flip()
                if fre_fix1[i % len(fre_fix1)] == 1: 
                    self.mywin.flip()
                    self.pattern1.setAutoDraw(False)
                    self.pattern2.setAutoDraw(True)
                    save_to_csv(f'data_{fre1}.csv', 1)
                    signal.append([1,datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')])
                elif fre_fix1[i % len(fre_fix1)] == 0:
                    self.mywin.flip()
                    self.pattern2.setAutoDraw(False)
                    save_to_csv(f'data_{fre1}.csv', 0)
                    signal.append([0,datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')])
                i += 1
            frequency = calculate_frequency(signal)
            print(f'Frequency = {frequency}')
            print(f'END time {t_start.getTime()}')
            print(f'END trail {count_trial} in {fre1} Hz ')
            self.fixation.setAutoDraw(False)     
            self.pattern1.setAutoDraw(False)
            self.pattern2.setAutoDraw(False)

            # Trialclock = core.Clock()
            # self.text_break.setAutoDraw(True)
            # self.mywin.flip()
            # self.outlet.push_sample([0])
            # while True:
            #     if Trialclock.getTime() >= 5:
            #         break
            # self.text_break.setAutoDraw(False)
            # self.fixation.setAutoDraw(True)   

            # #self.outlet.push_sample
            # t_start = core.Clock()
            # i = 0
            # signal = []
            # while t_start.getTime() <= block_dur:
            #     # print(f'2 {i}')
            #     self.fixation.setAutoDraw(True)
            #     self.pattern3.setAutoDraw(True)
            #     self.mywin.flip()
            #     if fre_fix2[i % len(fre_fix2)] == 1:
            #         self.mywin.flip()
            #         self.pattern3.setAutoDraw(False)
            #         self.pattern4.setAutoDraw(True)
            #         save_to_csv(f'data_{fre2}.csv', 1)
            #         signal.append([1,datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')])
            #     elif fre_fix2[i % len(fre_fix2)] == 0:
            #         self.mywin.flip()
            #         self.pattern4.setAutoDraw(False)
            #         save_to_csv(f'data_{fre2}.csv', 0)
            #         signal.append([0,datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')])
            #     i += 1

            # self.fixation.setAutoDraw(False)     
            # self.pattern3.setAutoDraw(False)
            # self.pattern4.setAutoDraw(False)
            # frequency = calculate_frequency(signal)
            # print(f'Frequency = {frequency}')
            # print(f'END time {t_start.getTime()}')
            # print(f'END trail {count_trial} in {fre2} Hz ')

            # Trialclock = core.Clock()
            # self.text_break.setAutoDraw(True)
            # self.mywin.flip()
            # self.outlet.push_sample([0])
            # while True:
            #     if Trialclock.getTime() >= 5:
            #         break
            # self.text_break.setAutoDraw(False)
            # self.fixation.setAutoDraw(True) 

            # self.outlet.push_sample([0])
            # t_start = core.Clock()
            # i = 0
            # signal = []
            # while t_start.getTime() <= block_dur:
            #     # print(f'3 {i}')
            #     self.fixation.setAutoDraw(True)
            #     self.pattern5.setAutoDraw(True)
            #     self.mywin.flip()
            #     if fre_fix3[i % len(fre_fix3)] == 1:
            #         self.mywin.flip()
            #         self.pattern5.setAutoDraw(False)
            #         self.pattern6.setAutoDraw(True)
            #         save_to_csv(f'data_{fre3}.csv', 1)
            #         signal.append([1,datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')])
            #     elif fre_fix3[i % len(fre_fix3)] == 0:
            #         self.mywin.flip()
            #         self.pattern6.setAutoDraw(False)
            #         save_to_csv(f'data_{fre3}.csv', 0)
            #         signal.append([0,datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')])
            #     i += 1

            # self.fixation.setAutoDraw(False)     
            # self.pattern5.setAutoDraw(False)
            # self.pattern6.setAutoDraw(False)
            # frequency = calculate_frequency(signal)
            # print(f'Frequency = {frequency}')
            # print(f'END time {t_start.getTime()}')
            # print(f'END trail {count_trial} in {fre3} Hz ')

            # Trialclock = core.Clock()
            # self.text_break.setAutoDraw(True)
            # self.mywin.flip()
            # self.outlet.push_sample([0])
            # while True:
            #     if Trialclock.getTime() >= 5:
            #         break
            # self.text_break.setAutoDraw(False)
            # self.fixation.setAutoDraw(True) 

            # #self.outlet.push_sample
            # t_start = core.Clock()
            # i = 0
            # signal = []
            # while t_start.getTime() <= block_dur:
            #     # print(f'4 {i}')
            #     self.fixation.setAutoDraw(True)
            #     self.pattern7.setAutoDraw(True)
            #     self.mywin.flip()
            #     if fre_fix4[i % len(fre_fix4)] == 1:
            #         self.mywin.flip()
            #         self.pattern7.setAutoDraw(False)
            #         self.pattern8.setAutoDraw(True)
            #         save_to_csv(f'data_{fre4}.csv', 1)
            #         signal.append([1,datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')])
            #     elif fre_fix4[i % len(fre_fix4)] == 0:
            #         self.mywin.flip()
            #         self.pattern8.setAutoDraw(False)
            #         save_to_csv(f'data_{fre4}.csv', 0)
            #         signal.append([0,datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')])
            #     i += 1

            # self.fixation.setAutoDraw(False)     
            # self.pattern7.setAutoDraw(False)
            # self.pattern8.setAutoDraw(False)
            # frequency = calculate_frequency(signal)
            # print(f'Frequency = {frequency}')
            # print(f'END time {t_start.getTime()}')
            # print(f'END trail {count_trial} in {fre4} Hz ')
            # Trialclock = core.Clock()
            # self.text_trial.setAutoDraw(True)
            # self.mywin.flip()
            # self.outlet.push_sample([0])
            # while True:
            #     if Trialclock.getTime() >= 5:
            #         break
            # self.text_trial.setAutoDraw(False)
            # self.fixation.setAutoDraw(False) 
            count_trial += 1
            if count_trial == num_trial:
                break
        # self.text_end.setAutoDraw(True)
        # self.mywin.flip()
        # # ##self.outlet.push_sample([0])
        # while True:
        #     if Trialclock.getTime() >= 5:
        #         break
        # self.text_end.setAutoDraw(False)
        # self.stop()

stimuli=SSVEP()
stimuli.start()