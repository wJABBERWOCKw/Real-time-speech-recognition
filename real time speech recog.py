#!/usr/bin/env python
# coding: utf-8

# In[39]:


import ipywidgets as widgets
from IPython.display import display
from threading import Thread
from queue import Queue


# In[43]:


record_button=widgets.Button(description="Record",disabled=False,button_style="success",icon="microphone")
stop_button=widgets.Button(description="Stop",disabled=False,button_style="warning",icon="stop")
output=widgets.Output()
messages =Queue()
recordings=Queue() #storing 
def start_recording(data):
    messages.put(True)
    with output:
        display("Starting...")
        record=Thread(target=record_microphone)
        record.start()
        
        transcribe=Thread(target=speech_recognition,args=(output,))
        transcribe.start()
def stop_recording(data):
    with output:
        messages.get()
        display("Stopped.")
        
record_button.on_click(start_recording)
stop_button.on_click(stop_recording)
display(record_button,stop_button,output)


# In[40]:


import pyaudio
p=pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))

p.terminate()


# In[41]:


CHANNELS=1
FRAME_RATE=16000
RECORD_SECONDS=8
AUDIO_FORMAT=pyaudio.paInt16
SAMPLE_SIZE=2
def record_microphone(chunk=1024):
    p=pyaudio.PyAudio()
    
    stream=p.open(format=AUDIO_FORMAT,
                  channels=CHANNELS,
                  rate=FRAME_RATE,
                  input=True,
                  input_device_index=1,
                  frames_per_buffer=chunk)
    
    frames=[]
    while not messages.empty():
        data=stream.read(chunk)
        frames.append(data)
        
        if len(frames)>=  (FRAME_RATE * RECORD_SECONDS)/chunk:
            recordings.put(frames.copy())
            frames=[]
            
    stream.stop_stream()
    stream.close()
    p.terminate()
            


# In[42]:


import subprocess
import json
from vosk import Model,KaldiRecognizer

model=Model(model_name="vosk-model-small-en-us-0.15")
rec=KaldiRecognizer(model,FRAME_RATE)
rec.SetWords(True)

def speech_recognition(output):
    while not messages.empty():
        frames=recordings.get()
        
        rec.AcceptWaveform(b''.join(frames))
        result=rec.Result()
        text=json.loads(result)["text"]
        
    


# In[ ]:




