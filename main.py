from PyQt5 import QtWidgets
from T4UI import Ui_MainWindow
import sys
import imagehash
import pickle
from scipy import signal
import wave
from scipy.io import wavfile
import matplotlib.pyplot as plot
import pylab
from scipy.signal import find_peaks
from PIL import Image
import os
import numpy as np
from PyQt5.QtWidgets import QMessageBox
import json 
from imagehash import hex_to_hash



class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.image=None
        self.hashBrowsedSong=None
        self.FirstSongData=[]
        self.SecondSongData=[]
        self.outputResultSingle=""
        self.outputResultMixed=""
        self.samplingFrequency=None
        self.mix_arr=[self.FirstSongData,self.SecondSongData]
        self.MixedSongData=None
        self.hashMixedSong=None

        self.ui.browseSong_Button.clicked.connect(self.Browse)
        self.ui.compareSongs_Button.clicked.connect(self.compareSingle)

        self.ui.firstSong_Button.clicked.connect(self.BrowseFirstSong)
        self.ui.secondSong_Button.clicked.connect(self.BrwoseSecondSong)

        #self.ui.percentageOfFirstSong_Slider.valueChanged.connect(self.checkMixing)
        self.ui.mix_Button.clicked.connect(self.checkMixing)
        self.ui.compareSongs_Button_2.clicked.connect(self.compareMixed)

    def compareSingle(self):
        self.compareWithDataBaseSongs(1)
    def compareMixed(self):
        self.compareWithDataBaseSongs(2)
    def BrowseFirstSong(self):
        self.BrowseMixture(0)

    def BrwoseSecondSong(self):
        self.BrowseMixture(1)
    def compareSongs(self,i):
        percentageOfSimilarity=0
        if(i==1):
            diff=self.hashBrowsedSong-self.hashSongDataBase
            percentageOfSimilarity=100-diff
        if(i==2):
            diff=self.hashMixedSong-self.hashSongDataBase
            percentageOfSimilarity=100-diff
        
        return percentageOfSimilarity

    def BrowseMixture(self,i):
        filepath= QtWidgets.QFileDialog.getOpenFileName()
        if(filepath[0]==""):
            self.show_popup("please select a song first")
            return
        wav1=wave.open(filepath[0],'r')
        frames=wav1.readframes(-1)
        self.mix_arr[i]=pylab.fromstring(frames,'Int16')
        if i==0:
            self.samplingFrequency1=wav1.getframerate()
        if i==1:
            self.samplingFrequency2=wav1.getframerate()

        samplingFrequency=wav1.getframerate()
        self.samplingFrequency=samplingFrequency
        if(len(self.mix_arr[i])<60*samplingFrequency):
            self.show_popup("choose a song at least 1 minute")
            return
        self.mix_arr[i]=(self.mix_arr[i])[0:60*samplingFrequency]

        wav1.close

    def checkMixing(self):


        if(len(self.mix_arr[0])==0 and len(self.mix_arr[1])==0):
            self.show_popup("both songs are empty")
            return

        if self.samplingFrequency1<self.samplingFrequency2:
            self.samplingrateofmixing=self.samplingFrequency1
        else:
            self.samplingrateofmixing=self.samplingFrequency2



        value=self.ui.percentageOfFirstSong_Slider.value()/100




        self.MixedSongData= value*self.mix_arr[0][:60*self.samplingrateofmixing]+(1-value)*self.mix_arr[1][:60*self.samplingrateofmixing]
        self.hashMixedSong=self.saveSpectrogram_Peaks_for_MixedSong(self.MixedSongData,int(self.samplingrateofmixing))


    def saveSpectrogram_Peaks_for_MixedSong(self,MixedSongData,samplingFrequency):
        plot.figure(num=None,figsize=(19,12))
        plot.style.use("dark_background")
        figure=plot.subplot(111)
        figure.get_xaxis().set_visible(False)
        figure.get_yaxis().set_visible(False)
        spectrogram=pylab.specgram(MixedSongData,Fs=samplingFrequency)
        pylab.savefig("MixedSong"+"Spectrogram.png",bbox_inches='tight')
        Array_1D=spectrogram[0].flatten()
        return self.peaks(Array_1D,"MixedSong")

        
        
    def Browse(self):
        filepath= QtWidgets.QFileDialog.getOpenFileName()
        print(filepath)
        if(filepath[0]==""):
            self.show_popup("please select a song first")
            return
        self.outputResultSingle=""
        self.hashBrowsedSong=self.saveSpectrogram_Peaks(filepath[0],"BrowsedSong")
        print("hashing>> ")
        print(type(self.hashBrowsedSong)
)
        print(self.hashBrowsedSong)

      
    def saveSpectrogram_Peaks(self,filepath,imagename):
        wav1=wave.open(filepath,'r')
        #samplingFrequency, signalData = wavfile.read(filepath[0])
        frames=wav1.readframes(-1)
        signalData=pylab.fromstring(frames,'Int16')

        samplingFrequency=wav1.getframerate()
        wav1.close
        if(len(signalData)<60*samplingFrequency):
            self.show_popup("choose a song at least 1 minute")
            return
        signalData=signalData[0:60*samplingFrequency]
        
        spectrogram=pylab.specgram(signalData,Fs=samplingFrequency)


        spectrogramArray=spectrogram[0]
        Array_1D=spectrogramArray.flatten()

        return self.peaks(Array_1D,imagename)

    def peaks(self,Array_1D,imagename):
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
    
        return hash
        

    def compareWithDataBaseSongs(self,i):
        

        if(i==1):
            if(self.hashBrowsedSong==None):
                self.show_popup("Browse a Song First!")
                return
            self.outputResultSingle+="The Similiraty Percentages for all songs in database are: " + "\n\n\n"
        if(i==2):
            if(self.hashMixedSong==None):
                self.show_popup("Browse Songs First!")
                return
            self.outputResultMixed+="The Similiraty Percentages for all songs in database are: " + "\n\n\n"


        file = open('data.json',)
        data = json.load(file)
        for song in data['song']:
            self.hashSongDataBase=hex_to_hash(song["hashvaule"])
            percentageOfSimilarity=self.compareSongs(i)
            if(i==1):
                self.outputResultSingle = self.outputResultSingle + song["name"] + " : " + str(percentageOfSimilarity) + "\n"
                self.ui.resultsTextBrowser.setText(self.outputResultSingle)
            if(i==2):
                self.outputResultMixed = self.outputResultMixed + song["name"] + " : " + str(percentageOfSimilarity) + "\n"
                self.ui.resultsTextBrowser_3.setText(self.outputResultMixed)


        



    def show_popup(self,string):
        message= QMessageBox()
        #logging.warning(string)
        message.setWindowTitle("Task4 Error Message")
        message.setText(string)
        #message.setIcon(QMessageBox.critical)
        x=message.exec_()
        

def main():
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    app.exec_()


if __name__ == "__main__":
    main()