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
        self.record_time = 3                                   #GUİ'deki 'Kayıt Süresi' değişkeni olarak yazan sayı
        self.new_rcrd_time = 3                                 #GUİ'deki 'Yeni Kayıt Süresi' değişkeni olarak yazan
        self.recording_name = 'Konuşma' #GUİ                   #GUİ'deki 'Yeni Ses Kaydet' yazısının yanındaki kutucukta yazan kelime
        self.fs = 16000                                        #Örnekleme frekansı değeri (frequence samples)
        self.frm = tk.Frame(win)
        save_record_bttn = tk.Button(self.frm, text = 'Yeni Ses Kaydet',command = self.new_record_func)     #'Yeni Ses Kaydet' butonu
        self.save_record_entry = tk.Entry(self.frm)
        self.record_list_bttn = tk.Button(self.frm,text = 'Kayıt Listesi',command = self.show_rec_list)     #'Kayıt listesi' butonu
        self.del_record_bttn = tk.Button(self.frm,text = 'Kaydı Sil',command = self.del_record_func)        #'Kayıt Sil' butonu
        sv_rcrd_t_label = tk.Label(self.frm, text = 'Yeni Kayıt Süresi (s): ')                              #Kayıt süresi belirleme
        self.sv_rcrd_t_entry = tk.Entry(self.frm)
        record_bttn = tk.Button(self.frm,text = 'Ses Al',command = self.calculate)                          #'Ses Al' butonu
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

    def del_record_func(self):                                              #Kayıtlı ses dosyasını silme fonksiyonu
        del_string = 'rm -f ./Records/'+ self.recording_name +'.wav'        #Girelen isimli wav dosyasının alır ve
        os.system(del_string)                                               #Ses dosyasını siler.

    def show_rec_list(self):                                                 #Kayıtlı olan ses dosyalarını görüntüleme fonksiyonu
        recording_names = os.listdir('./Records/')                           #'Records' isimli klasörün içine erişir ve içindeki dosyaların ismini alır.
        recording_names.sort()                                               #İçindeki dosyaları alfabetik sıraya göre dizer.
        recorded_voices = ''                                                 #Boş bir string değişkeni tanımlanır.
        for item in recording_names:
            item = item[0:-4]
            recorded_voices += item + '\n'                                   #Tanımlanan string değişkenini içine, satır şeklinde dosya isimlerini yazar.

        messagebox.showinfo("Kaydedilen Kayıtlar",recorded_voices)          #Dosya isimlerini alfabetik olarak sıralanmış şekilde ekrana yazdırır.


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

    def get_rec_name(self,*args):                                                                            # Ses dosyası ismini alan fonksiyon
        self.recording_name = self.save_record_entry.get()

    def new_record_func(self):                                                                              #Ses kaydetme fonksiyonu (GUİ'deki 'Yeni Ses Kaydet' tuşu işlevi)
        record_voice = sounddevice.rec(int(self.new_rcrd_time * self.fs),samplerate=self.fs,channels = 2)   #Ses kaydetme aşaması; değişkenler sırasıyla: 1- toplam frekans örneklemesi(fs), 2- Saniyedeki örnekleme frekansı, 3- kanal sayısı
        print('Yeni Ses kayıt ediliyor...')
        sounddevice.wait()
        t = time.localtime()
        current_time = time.strftime("%H_%M_%S",t)
        write('./Records/'+current_time+'.wav',self.fs,record_voice)                                        # Ses Alınıp kaydediliyor
        os.system('ffmpeg -i ./Records/'+ current_time+'.wav '+ './Records/'+self.recording_name+'.wav')    # ffmpeg kullanılarak ses wav formatına dönüştürülüyor.
        os.system('rm -f ./Records/'+ current_time+'.wav')                                                  # Dönüştürüldükten sonra eski kayıt siliniyor
        self.identify_label['text'] = 'Yeni Ses Alındı.'                                                    #Sesin başarılı bir şekilde alındığını belirten yazı
        recording_names = os.listdir('./Records/')
        self.show_rec_list()


    def calculate(self):                                                                                    # Anlık olarak alınan sesin mevcut ses dosyaları ile karşılaştırılarak en uyumulu ses dosyasını belirleme
        recording_names = os.listdir('./Records/')                                                          #'Records' klasörünün içindeki dosyaların isimlerini bir değişkene atama ve
        recording_names.sort()                                                                              #Dosya isimlerini alfabetik olarak sıralama
        t_record,data_record = self.record_audio(self.record_time,self.fs)                                  #Anlık olarak kaydedilen sesin kayıt süresini ve verileni alma
        number_of_recordings = len(recording_names)
        pre_emphasis = 0.97
        data_record = np.append(data_record[0],data_record[1:] -pre_emphasis * data_record[:-1])             #Kaydedilen veriye önce önvurgu(preemphasis) işlemi yapılır. Ön vurgu filtresinin amacı sinyalin yüksek frekans spektrumuna ilişkin enerjisinin arttırılmasıdır.
        data_record = data_record * np.hamming(np.size(data_record))                                        #Daha sonra veriye hamming işlemi uygulanır. Buradaki amaç yine gürültüleri yok etmektir.
        f_record, Y_record = self.fourier_t(t_record,data_record,self.fs)                                   #Sonra verilerin 'fft'si alınır.
        cor_matrix = []                                                                                     #Boş bir matris oluşturma
        i = 1

        for item in recording_names:                                                                                            # 'Records' klasöründe kaydedilen sesler alınır ve
            exec1 = "t"+str(i)+",data"+str(i)+",fs"+str(i)+" = self.open_sound('./Records/'+item)"                              #Sırasıyla değer ve kayıt süreleri değişkenlere atanır.
            exec(exec1) 
            exec1_5 = "data"+str(i)+" = np.append(data"+str(i)+"[0],data"+str(i)+"[1:] -pre_emphasis * data"+str(i)+"[:-1])"    #Önce önvurgu (preemphasis) işlemine
            exec(exec1_5)
            exec1_7 = "data"+str(i)+" = data"+str(i)+" * np.hamming(np.size(data"+str(i)+"))"                                    #Daha sonra hamming işlemine tabi tutulur.
            exec(exec1_7)
            exec2 = "f"+str(i)+",Y"+str(i)+" = self.fourier_t(t"+str(i)+",data"+str(i)+",fs"+str(i)+")"                         #Bu işlemlerden sonra 'fft'si alınır ve
            exec(exec2)
            exec3 = "cor"+str(i)+" = self.find_cor_ft(Y"+str(i)+",f"+str(i)+",Y_record,f_record)"                               #Anlık olarak kayıt edilen ses ve 'Records' klasöründen alınan ses dosyası verileri karşılaştırılır ve bir katsayı elde edilir.
            exec(exec3)
            exec4 = "cor_matrix.append([cor"+str(i)+",item])"                                                                   #Alınan katsayı uyum ile oratılıdır. Ne kadar fazla ise seslerin birbiri ile uyumu o kadar fazladır.
            exec(exec4)
            i += 1

        cor_matrix = sorted(cor_matrix, key = self.getKey,reverse = True)
        i = 1
        for item in recording_names:                                                                                            # Karşılaştırılan veriler kullanıcıya gösterilir
            exec5 = "label"+str(i)+ " = tk.Label(self.frm,text = cor_matrix[i-1][1]+': '+str(cor_matrix[i-1][0]))"
            exec(exec5)
            exec6 = "label"+str(i)+".grid(row = i+5,column = 0, columnspan = 2)"
            exec(exec6)
            i += 1

        self.identify_label['text'] = 'Algılanan Ses: '+cor_matrix[0][1]                                                        #Katsayı değeri en fazla olan ses ekrana yazdırılır.

    def getKey(self,item):
        return item[0]


    def open_sound(self,file_name):                                                                                             #Kayıtlı olan ses dosyalarının verilerine erişmek
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

    def record_audio(self,second,fs):                                                                                            #Anlık ses alma fonksiyonu (GUİ'deki 'Ses Al' tuşu işlevi)
        print('Kayıt Ediliyor...')
        record_voice = sounddevice.rec(int(second*fs),samplerate=fs,channels = 1)
        sounddevice.wait()
        record_voice = np.copy(record_voice)
        record_voice = record_voice[:,0]
        t = np.linspace(0,second,len(record_voice))
        self.identify_label['text'] = 'Ses Alındı.'
        return t,record_voice

    def fourier_t(self,t,data,fs):                                                                                                #fft alma fonksiyonu
        freqs = fs* fftfreq(len(t))
        mask = freqs > 0
        Y = (1/fs)*fft(data)
        Y = Y/ max(abs(Y))
        Y = Y[mask]
        freqs = freqs[mask]
        return freqs,Y


    def find_cor_ft(self,Y1,f1,Y2,f2):        #Anlık olarak alınan ses ile kayıtlı ses dosyalarının uyum katsayılarını belirleme
        thval = 0.05                          # Thereshold değerinin altındaki değerler hesaba katılmaz.
        inc1 = f1[1]-f1[0]                    # Incrementler frekans eksenlerinin uyumunu kontrol etmek için bulunur.
        inc2 = f2[1]-f2[0]
        if inc2 == inc1:                       # Frekans incrementleri eşit ise doğrudan kıyaslama yapılacak new Y1 ve new Y2 mask ile alınır.
            mask = abs(Y1) > thval
            newY1 = abs(Y1[mask])
            newY2 = abs(Y2[mask])
        elif inc2 < inc1:                   # inc2 inc1 den küçükse  f_ind ile f1 deki indislerin f2 ye göre değerleri bulunur ve new Y2 ona göre elde edilir
            mask = abs(Y1) > thval
            ratio = inc2/inc1
            f_ind = ratio*(f1[mask]//inc1-1)
            f_ind = f_ind.astype(dtype = 'uint16')
            newY2 = np.copy(Y1[mask])
            i= 0
            for item in f_ind:
                newY2[i] = (Y2[item])
                i += 1
            newY1 = Y1[mask]
        else:                              # inc2 nin inc1 den küçük olması durumudur elif'in içindeki yapının tersi yapılır.
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

        Y3 = abs(newY2) / abs(newY1)               # Elde edilen newY2 newY1 e bölünerek oranlar alınır.
        i = 0
        for item in Y3:                             # Oranların arasında 1 den büyük varsa tersi alınarak 1 den küçük olması sağlanır.
            if item > 1:
                Y3[i] = 1/Y3[i]
            i += 1
        cor = sum(Y3)/i                             # Tüm oranlar toplanır ve oran sayısına bölünür bu 0 ile 1 arasında bir sayı verecektir.
        return cor





win = tk.Tk()
win.title('Speaker Recognition APP v1')
prog = MyProgram(win)
win.mainloop()
