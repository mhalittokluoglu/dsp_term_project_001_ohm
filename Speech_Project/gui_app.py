import tkinter as tk
import wave
import numpy as np
from numpy.fft import fft, fftfreq, ifft
import sounddevice
from scipy.io.wavfile import write
import time
import os
from tkinter import messagebox


class MyProgram:
    def __init__(self,win):
        self.record_time = 10
        self.new_rcrd_time = 10
        self.recording_name = 'Konuşma'
        self.fs = 16000
        self.frm = tk.Frame(win)
        save_record_bttn = tk.Button(self.frm, text = 'Yeni Ses Kaydet',command = self.new_record_func)
        self.save_record_entry = tk.Entry(self.frm)
        self.record_list_bttn = tk.Button(self.frm,text = 'Kayıt Listesi',command = self.show_rec_list)
        self.del_record_bttn = tk.Button(self.frm,text = 'Kaydı Sil',command = self.del_record_func)
        sv_rcrd_t_label = tk.Label(self.frm, text = 'Yeni Kayıt Süresi (s): ')
        self.sv_rcrd_t_entry = tk.Entry(self.frm)
        record_bttn = tk.Button(self.frm,text = 'Ses Al',command = self.calculate)
        duration_label = tk.Label(self.frm,text = 'Kayıt Süresi (s):')
        self.duration_entry = tk.Entry(self.frm)

        self.identify_label = tk.Label(self.frm,text ='',font = 'Times 16 bold')

        self.sv_rcrd_t_entry.insert(0,str(self.new_rcrd_time))
        self.duration_entry.insert(0,str(self.record_time))
        self.save_record_entry.insert(0,str(self.recording_name))

        self.save_record_entry.bind("<Return>", self.get_rec_name)
        self.sv_rcrd_t_entry.bind("<Return>", self.save_rcrd_func)
        self.duration_entry.bind("<Return>", self.get_dr_func)


        self.frm.grid(row = 0, column = 0)
        save_record_bttn.grid(row = 0, column = 0)
        self.save_record_entry.grid(row = 0, column = 1)
        self.record_list_bttn.grid(row = 1, column = 0)
        self.del_record_bttn.grid(row = 1, column = 1)
        sv_rcrd_t_label.grid(row = 2, column = 0)
        self.sv_rcrd_t_entry.grid(row = 2, column = 1)
        record_bttn.grid(row = 3, column = 0, columnspan = 2)
        duration_label.grid(row = 4, column = 0)
        self.duration_entry.grid(row = 4, column = 1)
        self.identify_label.grid(row = 5, column = 0, columnspan = 2)

    def del_record_func(self):
        del_string = 'rm -f ./Records/'+ self.recording_name +'.wav'
        os.system(del_string)

    def show_rec_list(self):
        recording_names = os.listdir('./Records/')
        recording_names.sort()
        recorded_voices = ''
        for item in recording_names:
            item = item[0:-4]
            recorded_voices += item + '\n'

        messagebox.showinfo("Kaydedilen Kayıtlar",recorded_voices)


    def save_rcrd_func(self,*args):
        try:
            time1 = int(self.sv_rcrd_t_entry.get())
            if time1 > 0:
                self.new_rcrd_time = time1
        except ValueError:
            pass

    def get_dr_func(self,*args):
        try:
            time1 = int(self.duration_entry.get())
            if time1 > 0:
                self.record_time = time1
        except ValueError:
            pass

    def get_rec_name(self,*args):
        self.recording_name = self.save_record_entry.get()

    def new_record_func(self):
        record_voice = sounddevice.rec(int(self.new_rcrd_time * self.fs),samplerate=self.fs,channels = 2)
        print('Yeni Ses kayıt ediliyor...')
        sounddevice.wait()
        t = time.localtime()
        current_time = time.strftime("%H_%M_%S",t)
        write('./Records/'+current_time+'.wav',self.fs,record_voice)
        os.system('ffmpeg -i ./Records/'+ current_time+'.wav '+ './Records/'+self.recording_name+'.wav')
        os.system('rm -f ./Records/'+ current_time+'.wav')
        self.identify_label['text'] = 'Yeni Ses Alındı.'
        recording_names = os.listdir('./Records/')
        self.show_rec_list()


    def calculate(self):
        recording_names = os.listdir('./Records/')
        recording_names.sort()
        t_record,data_record = self.record_audio(self.record_time,self.fs)
        f_record, Y_record = self.fourier_t(t_record,data_record,self.fs)
        number_of_recordings = len(recording_names)


        cor_matrix = []
        i = 1

        for item in recording_names:
            exec1 = "t"+str(i)+",data"+str(i)+",fs"+str(i)+" = self.open_sound('./Records/'+item)"
            exec(exec1)
            exec2 = "f"+str(i)+",Y"+str(i)+" = self.fourier_t(t"+str(i)+",data"+str(i)+",fs"+str(i)+")"
            exec(exec2)
            exec3 = "cor"+str(i)+" = self.find_cor_ft(Y"+str(i)+",f"+str(i)+",Y_record,f_record)"
            exec(exec3)
            exec4 = "cor_matrix.append([cor"+str(i)+",item])"
            exec(exec4)
            i += 1

        cor_matrix = sorted(cor_matrix, key = self.getKey,reverse = True)
        i = 1
        for item in recording_names:
            exec5 = "label"+str(i)+ " = tk.Label(self.frm,text = cor_matrix[i-1][1]+': '+str(cor_matrix[i-1][0]))"
            exec(exec5)
            exec6 = "label"+str(i)+".grid(row = i+5,column = 0, columnspan = 2)"
            exec(exec6)
            i += 1

        self.identify_label['text'] = 'Algılanan Ses: '+cor_matrix[0][1]

    def getKey(self,item):
        return item[0]


    def open_sound(self,file_name):
        audio_1 = wave.open(file_name)
        frames = audio_1.getnframes()
        fs = audio_1.getframerate()
        duration = frames/float(fs)

        data = audio_1.readframes(-1)
        w_data = (1/fs)*np.frombuffer(data,np.int16)
        w_data.shape = -1,2

        audio_data = w_data[:,1]
        t = np.linspace(0,duration,len(audio_data))
        return t,audio_data,fs

    def record_audio(self,second,fs):
        print('Kayıt Ediliyor...')
        record_voice = sounddevice.rec(int(second*fs),samplerate=fs,channels = 1)
        sounddevice.wait()
        record_voice = np.copy(record_voice)
        record_voice = record_voice[:,0]
        t = np.linspace(0,second,len(record_voice))
        self.identify_label['text'] = 'Ses Alındı.'
        return t,record_voice

    def fourier_t(self,t,data,fs):
        freqs = fs* fftfreq(len(t))
        mask = freqs > 0
        Y = (1/fs)*fft(data)
        Y = Y/ max(abs(Y))
        Y = Y[mask]
        freqs = freqs[mask]
        return freqs,Y


    def find_cor_ft(self,Y1,f1,Y2,f2):
        thval = 0.5
        inc1 = f1[1]-f1[0]
        inc2 = f2[1]-f2[0]
        if inc2 == inc1:
            mask = abs(Y1) > thval
            newY1 = abs(Y1[mask])
            newY2 = abs(Y2[mask])
        elif inc2 < inc1:
            mask = Y1 > thval
            ratio = inc2/inc1
            f_ind = ratio*(f1[mask]//inc1-1)
            f_ind = f_ind.astype(dtype = 'uint16')
            newY2 = np.copy(Y1[mask])
            i= 0
            for item in f_ind:
                newY2[i] = (Y2[item])
                i += 1
            newY1 = Y1[mask]
        else:
            ratio = inc1/inc2
            f_ind = ratio*(f2//inc1-1)
            f_ind = f_ind.astype(dtype ='uint16')
            newY1 = np.copy(Y2)
            i = 0
            for item in f_ind:
                newY1[i]  = Y1[item]
                i += 1
            mask = newY1 > thval
            newY1 = newY1[mask]
            newY2 = Y2[mask]

        Y3 = abs(newY2) / abs(newY1)
        i = 0
        for item in Y3:
            if item > 1:
                Y3[i] = 1/Y3[i]
            i += 1
        cor = sum(Y3)/i
        return cor





win = tk.Tk()
win.title('Speaker Recognition APP v1')
prog = MyProgram(win)
win.mainloop()
