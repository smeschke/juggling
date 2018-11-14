from midiutil import MIDIFile
#if module error, try: sudo-apt get install python-scipy
import cv2
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import scipy.signal as signal

#path to source data
data_source = '/home/stephen/Desktop/sound1/sound.csv'
df = pd.read_csv(data_source)

times = []

#get column names
cols = []
for i in df: cols.append(i)

for bbb in range(int(len(cols)/2)):
    #plot data
    col = bbb*2+1
    peak_data = []
    #smooth it out
    smoothed_data = []
    window_length, polyorder = 21, 2
    YS = signal.savgol_filter(df[cols[col]], window_length, polyorder)
    #plot signal peaks
    peaks =  signal.find_peaks_cwt(YS, np.arange(15,20))
    #print(list(peaks))
    for peak in peaks:
        plt.scatter(peak, YS[peak],s=30)
        peak_data.append(peak)
    plt.plot(YS)
    #show signal peaks plot
    plt.show()

    peak_data.sort()
    testdata=[]
    for i in range(len(peak_data)-1):
        testdata.append((peaks[i], abs(peak_data[i+1]-peak_data[i])))
    times.append(testdata)

track    = 0
channel  = 0
time     = 0    # In beats
duration = 15    # In beats
tempo    = 120*60   # In BPM
volume   = 123  # 0-127, as per the MIDI standard

MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                      # automatically)
MyMIDI.addTempo(track, time, tempo)


for time_list in times:
    for t in time_list:
        track = 0
        channel = 0
        time = t[0]
        dist_val = t[1]
        duration = dist_val/3
        pitch = int(dist_val/2.5)
        MyMIDI.addNote(track, channel, pitch, time, 10, 100)

with open("/home/stephen/Desktop/scale.mid", "wb") as output_file:
    MyMIDI.writeFile(output_file)
