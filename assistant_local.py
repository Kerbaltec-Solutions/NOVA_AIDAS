import sys
import threading
import time
import subprocess
from pynput import keyboard
import settings
import llm
import ui_app
import overwrites


# Initialize LM Studio client
model_name_or_path = settings.LLM_MODEL

talk=True

nova = llm.LLM()
vars = ui_app.Vars()



def run_tkinter_app():
    """Function to start and manage the Tkinter application."""
    app = ui_app.App(nova,vars)
    app.mainloop()

def async_task():
    while not vars.exit:
        time.sleep(0.1)
        
        if(vars.listen):
            nova.message(overwrites.input())
            #app.update_text()

def chat_loop():
    subprocess.Popen("ollama serve", stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
    #subprocess.Popen("ollama run "+model_name_or_path, shell=True)

    listener = keyboard.Listener(on_release=lambda event: overwrites.on_release(event, nova))
    listener.start()
    
    tk_thread = threading.Thread(target=run_tkinter_app)
    tk_thread.start()

    main_thread = threading.Thread(target=async_task)
    main_thread.start()
    
    overwrites.print("Assistant started.")
    
    main_thread.join()

if __name__ == "__main__":
    chat_loop()

