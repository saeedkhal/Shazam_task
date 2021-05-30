import json 
import os
import imagehash
from PIL import Image 
import wave
import pylab
from scipy.signal import find_peaks
import numpy as np
import matplotlib.pyplot as plot
from imagehash import hex_to_hash



data={}
data["song"]=[]
directory=r"E:\\python projects\\dsp projects\\task4\\Dsp_task_song\\wavfolder\\data base songs" #the directory that have all songs with .wav extention
for i in os.listdir(directory):
    if i.endswith("wav"):
        imagename=os.path.splitext(i)[0]
        filepath=directory+"\\"+str(i)
        wav1=wave.open(filepath,'r')
        frames=wav1.readframes(-1)
        signalData=pylab.fromstring(frames,'Int16')
        samplingFrequency=wav1.getframerate()
        wav1.close
        signalData=signalData[0:60*samplingFrequency]
        spectrogram=pylab.specgram(signalData,Fs=samplingFrequency)
        spectrogramArray=spectrogram[0]
        Array_1D=spectrogramArray.flatten()
        base=os.path.basename(directory)


        plot.figure(num=None,figsize=(19,12))
        plot.style.use("dark_background")
        figure=plot.subplot(111)
        figure.get_xaxis().set_visible(False)
        figure.get_yaxis().set_visible(False)


        peaks, time_diff = find_peaks(Array_1D, distance=150)
        pylab.plot(Array_1D)
        pylab.plot(peaks, (Array_1D)[peaks], "x")
        pylab.plot(np.zeros_like(Array_1D), "--", color="red")
        pylab.savefig(imagename+'Peaks.png', bbox_inches='tight')
        image=Image.open(imagename+'Peaks.png')
        hash=imagehash.phash(image)
        data["song"].append({"name":imagename,"hashvaule":str(hash)})


with open('data.json', 'w') as outfile:
    json.dump(data, outfile)

print(type(data["song"][1]["hashvaule"]))
x=hex_to_hash(data["song"][1]["hashvaule"])
print(type(x))


 
