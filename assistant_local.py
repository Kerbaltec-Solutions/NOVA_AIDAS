import sys
import threading
import time
import subprocess
import logging
import contextlib
import builtins
from pynput import keyboard
from pynput.keyboard import Key
from RealtimeSTT import AudioToTextRecorder
from RealtimeTTS import TextToAudioStream, PiperEngine, PiperVoice
import settings
import llm
import ui_app

# Initialize LM Studio client
model_name_or_path = settings.LLM_MODEL

model_name="cori-high"

engine = PiperEngine(
    piper_path="./piper/piper",
    voice=PiperVoice(
        model_file="./"+model_name+".onnx",
        config_file="./"+model_name+".onnx.json",
    )
)


stream = TextToAudioStream(engine, language = "en", level=logging.FATAL, frames_per_buffer=1000)

talk=True

nova = llm.LLM()
vars = ui_app.Vars()

def on_release(key):
    global talk
    if(key==Key.page_up):
        talk=False
        stream.stop()
    if(key==Key.page_down):
        talk=False
        stream.stop()
        nova.message(input(overwrite="True"))
        #app.update_text()
    return

def print(text: str):
    if(vars.text_mode):
        builtins.print(text)
        return
    global talk
    global stream
    talk=True
    
    for sub in text.replace('\\n', '\n').replace('\\t', '\t').replace('\\','').replace('*',' ').split("\n"):
        for sentence in sub.split("..."):
            if(sentence!=""):
                stream.feed(sentence)
                stream.play(language="en", buffer_threshold_seconds=1, log_synthesized_text=True, sentence_fragment_delimiters="", force_first_fragment_after_words=50)
                if(not talk):
                    stream.stop()
                    return

def input(prompt="", overwrite=False):
    if(vars.text_mode and not overwrite):
        return(builtins.input(prompt))

    print(prompt)
    
    with AudioToTextRecorder(model="tiny.en", language="en", post_speech_silence_duration=1) as recorder:
        with contextlib.redirect_stdout(None):
            text=recorder.text()
        builtins.print("\033[1m\033[92m⚡ synthesizing\033[0m → \'"+text+"\'")
        return(text)

def run_tkinter_app():
    """Function to start and manage the Tkinter application."""
    app = ui_app.App(nova,vars)
    app.mainloop()

def async_task():
    while not vars.exit:
        time.sleep(0.1)
        
        if(vars.listen):
            nova.message(input())
            #app.update_text()

def chat_loop():
    subprocess.Popen("ollama serve", stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
    #subprocess.Popen("ollama run "+model_name_or_path, shell=True)

    listener = keyboard.Listener(on_release=on_release)
    listener.start()
    
    tk_thread = threading.Thread(target=run_tkinter_app)
    tk_thread.start()

    main_thread = threading.Thread(target=async_task)
    main_thread.start()
    
    print("Assistant started.")
    
    main_thread.join()

if __name__ == "__main__":
    chat_loop()

