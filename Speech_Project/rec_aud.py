import sounddevice
from scipy.io.wavfile import write
import time
import os

fs = 16000
second = 3
print('Recording')
record_voice = sounddevice.rec(int(second * fs),samplerate=fs,channels = 2)
sounddevice.wait()

t = time.localtime()
current_time = time.strftime("%H_%M_%S",t)
write(current_time+'.wav',fs,record_voice)
os.system('ffmpeg -i '+ current_time+'.wav 5.wav')
os.system('rm -f '+ current_time+'.wav')
