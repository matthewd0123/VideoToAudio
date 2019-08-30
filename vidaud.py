from __future__ import print_function
import cv2
import pyaudio
import numpy as np
import random
import time
import scipy.io.wavfile
import wave
import soundfile as sf
import wavio
import subprocess
import random

def sin_func(data, mod, t, amp):
    return amp*np.sin((2+mod)*np.pi * data * t)

def notes_with_overtones(data, first, second, third, seventh, half,  mod, t, amp):
    ampMod = 1
    if (data > 300):
        ampMod = 2
    if (data > 400):
        ampMod = 4
    if (data > 500):
        ampMod = 8
    return (amp/2)*np.sin((2+mod)*np.pi * data * t) + (amp/4)*np.sin((2+mod)*np.pi * half * t) + (amp/8)*np.sin((2+mod)*np.pi * first * t) + (amp/16)*np.sin((2+mod)*np.pi * second * t) + (amp*ampMod/32)*np.sin((2+mod)*np.pi * third * t) + (amp*ampMod/64)*np.sin((2+mod)*np.pi * seventh * t)
yellowFirstBound = 200
greenFirstBound = 120
blueFirstBound = greenFirstBound

greenScalar = 25

noiseLimit = 0.001

modMod = 0.0005

output_wav = "audio.wav"
input_vid = 'nature.mp4'

vidcap = cv2.VideoCapture(input_vid)
success,image = vidcap.read()
fps = vidcap.get(cv2.CAP_PROP_FPS)
count = 0
image_list = []
while success:
  success,image = vidcap.read()
  count += 1
  image_list.append(image)

avg_intensity = []
yellowList = []
yellowList2 = []
yellowList3 = []
greenList = []
blueList = []

for frame in image_list:
    pixel_count  = 0
    red = 0
    green = 0
    blue = 0
    NoneType = type(None)
    if not isinstance(frame, NoneType):
        for colors in frame[0]:
            pixel_count += 1
            red += colors[0]
            green += colors[1]
            blue += colors[2]
        avg_intensity.append((red+green+blue)/pixel_count)
        yellowIntensity = (red+green)/pixel_count
        greenIntensity = green/pixel_count
        blueIntensity = blue/pixel_count
        if (yellowIntensity > yellowFirstBound):
            yellowList.append(0)
        else:
            yellowList.append(0)
        if (greenIntensity > greenFirstBound):
            greenList.append(1)
        else:
            greenList.append(0)
        if (blueIntensity > blueFirstBound):
            blueList.append(1)
        else:
            blueList.append(0)

#Frequency Conversion

avg_intensity = [x*1.0784+55 for x in avg_intensity]
avg_intensity_first = [x*2 for x in avg_intensity]
avg_intensity_second = [x*3 for x in avg_intensity]
avg_intensity_third = [x*4 for x in avg_intensity]
avg_intensity_seventh = [x*8 for x in avg_intensity]
avg_intensity_half = [x*0.5 for x in avg_intensity]

print(avg_intensity)

yellowList = [x*220 for x in yellowList]
yellowList2 = [x*225 for x in yellowList]
yellowList3 = [x*230 for x in yellowList]

for index, x in enumerate(greenList):
    if index > 0:
        if greenList[index-1] !=0 and greenList[index] != 0:
            greenList[index] = greenList[index-1] + greenScalar
            if greenList[index] > 900 or greenList[index]< 700:
                greenScalar = -greenScalar

for index, x in enumerate(blueList):
    if x != 0:
        blueList[index] = random.uniform(1000, 1200)


row_length  = 1000

lower_vol = 0
upper_vol = 1

lower_hz = 440
upper_hz = 880

lower_dur = 0.01
upper_dur = 0.5

volume = 0.5     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 1.0   # in seconds, may be float
f = 440.0        # sine frequency, Hz, may be float

freq_list1 = np.linspace(lower_hz, upper_hz, row_length)
random.shuffle(freq_list1)

freq_list2 = freq_list1
#freq_list2 = freq_list2[::-1]
random.shuffle(freq_list2)

dur_list1 = np.linspace(lower_dur, upper_dur, row_length)
random.shuffle(dur_list1)

dur_list2 = dur_list1
random.shuffle(dur_list2)

vol_list1 = np.linspace(lower_vol, upper_vol, row_length)
random.shuffle(vol_list1)

vol_list2 = np.linspace(lower_vol, upper_vol, row_length)
random.shuffle(vol_list1)


two_pi_range = np.linspace(0, np.pi, 100)

print("Step 1 Done")

rate = 44100  # samples per second
T = 1/fps         # sample duration (seconds)
f = 440.0     # sound frequency (Hz)
t = np.linspace(0, T, T*rate, endpoint=False)
x = np.sin(2*np.pi * avg_intensity[0] * t)
#print ('| avg_intensity  | YellowList  | GreenList  | BlueList  \n')
for index, l in enumerate(avg_intensity):
    #print ('|' + str(avg_intensity[index]) + '|' + str(yellowList[index]) + '|' + str(greenList[index]) + '|' + str(blueList[index]) + '|\n')
    print(str(100*float(index)/float(len(avg_intensity))) +' percent done!')
    appendee = np.zeros(len(sin_func(0, 0, t, 1)))
    appendee = notes_with_overtones(l, avg_intensity_first[index], avg_intensity_second[index], avg_intensity_third[index], avg_intensity_seventh[index], avg_intensity_half[index], 0, t, 0.4)+ sin_func(yellowList[index], 0, t, 0.2) + sin_func(yellowList2[index], 0, t, 0.2) + sin_func(yellowList3[index], 0, t, 0.2)  + sin_func(greenList[index], 0, t, 0.2) + sin_func(blueList[index], 0, t, 0.2)
    modifier = modMod
    while (abs(appendee[-1]) > noiseLimit):
        appendee = notes_with_overtones(l, avg_intensity_first[index], avg_intensity_second[index], avg_intensity_third[index], avg_intensity_seventh[index], avg_intensity_half[index], modifier, t, 0.4)+ sin_func(yellowList[index], modifier, t, 0.2) + sin_func(yellowList2[index], modifier, t, 0.2) + sin_func(yellowList3[index], modifier, t, 0.2)  + sin_func(greenList[index], modifier, t, 0.2) + sin_func(blueList[index], modifier, t, 0.2)
        modifier += modMod
    x = np.append(x, appendee)


wavio.write(output_wav, x, fs, sampwidth=3)

subprocess.call(["ffmpeg", "-i", input_vid, "-i", output_wav, "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0", "new_" + "mod_" + str(modMod) + "_noise_" + str(noiseLimit) + "_" + input_vid])
