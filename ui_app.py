import tkinter as tk
import settings
import pickle

class Vars():
    listen=False
    short_answer=True
    text_mode=True
    exit=False

class App(tk.Tk):
    vars=None
    def __init__(self,llm,vars):
        self.vars=vars
        self.nova = llm

        super().__init__()

        self.title("Computer Assistant")
        self.configure(background="black")
        self.bind("<Button-2>", self.handle_voice)
        self.resizable(0, 0) 
        
        self.log = tk.Text(background="black", wrap='word', highlightthickness=0, bd=0)
        self.log.grid(row=0, column=0, columnspan=5, sticky="nsew")
        self.log.tag_config('user', foreground="white")
        self.log.tag_config('nova', foreground="yellow")
        self.log.tag_config('system', foreground="red")

        tk.Label(background="black", foreground="white", bd=0, text="Input").grid(row=1, column=0, sticky="nsew", pady=5, padx=5)

        self.input = tk.Entry(background="gray", bd=0)
        self.input.bind("<Return>", self.handle_submit)
        self.input.grid(row=1, column=1, columnspan=3, sticky="nsew", pady=5, padx=5)

        self.submit = tk.Button(text="SUBMIT",background="gray", bd=0)
        self.submit.bind("<Button-1>", self.handle_submit)
        self.submit.grid(row=1, column=4, pady=5, padx=5)

        self.mode = tk.Button(text="MODE",background="gray", bd=0)
        self.mode.bind("<Button-1>", self.handle_mode)
        self.mode.grid(row=2, column=0, pady=5, padx=5)

        self.mode_d = tk.Label(background="black", foreground="white", bd=0)
        self.mode_d.grid(row=2, column=1, sticky="nsew", pady=5, padx=5)

        self.short = tk.Button(text="SHORT", bd=0)
        self.short.bind("<Button-1>", self.handle_short)
        self.short.grid(row=2, column=2, pady=5, padx=5)

        self.listening = tk.Button(text="LISTEN", bd=0)
        self.listening.bind("<Button-1>", self.handle_listen)
        self.listening.grid(row=2, column=3, pady=5, padx=5)

        self.voice = tk.Button(text="VOICE",background="gray", bd=0)
        self.voice.bind("<Button-1>", self.handle_voice)
        self.voice.grid(row=2, column=4, pady=5, padx=5)

        self.load = tk.Button(text="LOAD",background="gray", bd=0)
        self.load.bind("<Button-1>", self.handle_load)
        self.load.grid(row=3, column=0, pady=5, padx=5)

        self.save = tk.Button(text="SAVE",background="gray", bd=0)
        self.save.bind("<Button-1>", self.handle_save)
        self.save.grid(row=3, column=1, pady=5, padx=5)
        
        self.path = tk.Entry(background="gray", bd=0)
        self.path.grid(row=3, column=2, columnspan=2, sticky="nsew", pady=5, padx=5)
        self.path.insert(0,"log")

        self.clear = tk.Button(text="CLEAR",background="gray", bd=0)
        self.clear.bind("<Button-1>", self.handle_clear)
        self.clear.grid(row=3, column=4, pady=5, padx=5)

        self.get_state()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_state(self):
        if(self.vars.listen):
            self.listening.config(background="green")
        else:
            self.listening.config(background="gray")
        if(self.vars.short_answer):
            self.short.config(background="green")
        else:
            self.short.config(background="gray")
        if(self.vars.text_mode):
            self.mode_d.config(text="TEXT")
        else:
            self.mode_d.config(text="VOICE")

    def update_text(self):
        self.log.delete(1.0,tk.END)
        for message in self.nova.messages:
            content=message.get("content")
            if(content!=""):
                if(message.get("role") == "user"):
                    self.log.insert(tk.END, "You: "+content+"\n", 'user')
                elif(message.get("role") == "assistant"):
                    self.log.insert(tk.END, "Nova: "+content+"\n", 'nova')
                #elif(message.get("role") == "system"):
                #    self.log.insert(tk.END, "System: "+content+"\n", 'system')
        self.log.see(tk.END)
        self.update()

    def handle_submit(self, event):
        self.submit.config(background="red")
        inp=self.input.get()
        self.log.insert(tk.END, "You: "+inp+"\n", 'user')
        self.log.insert(tk.END, "Nova: THINKING...\n", 'nova')
        self.log.see(tk.END)
        self.input.delete(0,tk.END)
        self.update()
        r=self.nova.message(inp)
        if("ERROR:" in r):
            self.log.insert(tk.END, r+"\n", 'system')
            self.log.see(tk.END)
        else:
            self.update_text()
        if(self.vars.exit):
            self.destroy()
        self.submit.config(background="gray")

    def handle_listen(self, event):
        self.vars.listen=not self.vars.listen
        global tmp
        if(self.vars.listen):
            tmp=self.vars.text_mode
            self.vars.text_mode=False
        else:
            self.vars.text_mode=tmp
        self.get_state()

    def handle_voice(self, event):
        self.voice.config(background="red")
        inp=input(overwrite=True)
        self.log.insert(tk.END, "You: "+inp+"\n", 'user')
        self.log.insert(tk.END, "Nova: THINKING...\n", 'nova')
        self.log.see(tk.END)
        self.update()
        r=self.nova.message(inp)
        if("ERROR:" in r):
            self.log.insert(tk.END, r+"\n", 'system')
            self.log.see(tk.END)
        else:
            self.update_text()
        if(self.vars.exit):
            self.destroy()
        self.voice.config(background="gray")

    def handle_mode(self, event):
        self.vars.text_mode=not self.vars.text_mode
        self.get_state()

    def handle_short(self, event):
        self.vars.short_answer=not self.vars.short_answer
        self.get_state()

    def handle_save(self, event):
        file_path="./"+self.path.get()+".bin"
        print("\nSaving chat-log to "+file_path)
        with open(file_path, 'wb') as file:
            pickle.dump(self.nova.messages, file)

    def handle_load(self, event):
        file_path="./"+self.path.get()+".bin"
        try:
            print("\nLoading chat-log from "+file_path)
            with open(file_path, 'rb') as file:
                self.nova.messages[:] = pickle.load(file) + self.nova.messages
            self.update_text()
        except FileNotFoundError:
            print("\nFailed loading chat-log from "+file_path)

    def handle_clear(self, event):
        del self.nova.messages[:]
        self.nova.messages[:]=settings.PRIMER
        self.update_text()

    def on_closing(self):
        self.vars.exit=True
        self.destroy()