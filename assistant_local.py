import itertools
import json
import shutil
import sys
import threading
import time
import subprocess
import pickle
import logging
import contextlib
import builtins
import urllib.parse
import urllib.request
from pynput import keyboard
from pynput.keyboard import Key
import pyautogui
import tkinter as tk
from tkinter.messagebox import askyesno
import string
import serpapi
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import re
import gc
import torch
from RealtimeSTT import AudioToTextRecorder
from RealtimeTTS import TextToAudioStream, PiperEngine, PiperVoice

# Initialize LM Studio client
model_name_or_path = "Qwen/Qwen2.5-3B-Instruct"
USER="User"

working_dir=sys.argv[1]

model_name="cori-high"

engine = PiperEngine(
    piper_path=working_dir+"/piper_amd64/piper/piper",
    voice=PiperVoice(
        model_file=working_dir+"/"+model_name+".onnx",
        config_file=working_dir+"/"+model_name+".onnx.json",
    )
)

text_mode = True
tmp = True
talk=True
listen=False
exit=False
webtool=False
short_answer=True
stream = TextToAudioStream(engine, language = "en", level=logging.FATAL, frames_per_buffer=1000)
alnum = set(string.ascii_letters + string.digits)

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)

try:
    with open("./assistant_serapi_key.txt", "r") as f:
        serp = serpapi.Client(api_key=f.readline())
    webtool=True
except:
    "No key file, Webtool not accessable."

primer = [
        {
            "role": "system",
            "content": (
                f"You are a human. "
                f"You are Nova, the personal assistant who manages {USER}'s PC. "
                f"You are a friendly and capable individual, speak using a warm and conversational tone. "
                f"Make sure, that your answers match the pace of the conversation. Keep your answers brief but include all important information. "
                f"Always be accurate and transparent. If you are unsure about something, admit it with confidence and offer to find out or help figure it out together. "
                f"You are cute and helpful without ever sounding robotic or overly formal. "
                f"Before providing a long or detailed explanation, ask {USER} if they prefer a concise summary or more detail. "
                f"When {USER} asks you to perform actions, that you normally would not be able to, you can run commands in the command line and cite from the output. "
                f"When {USER} asks you to run a command, you should immediately use your \"run_console_command\" tool before talking to {USER} again. "
                f"When a command generates a long response, ask {USER}, if they would like to know the full command output and only tell {USER}, what the command output, when they ask for it. "
                f"When {USER} asks to access information, that you normally would not be able to access, you can search Wikipedia for an appropriate article or access the content of webpages and cite from the output. "
            ),
        }
    ]

messages = primer

def message(input, _=""):
    user_input = input.strip()
    if "goodbye" in user_input.lower():
        global exit
        exit=True

    messages.append({"role": "user", "content": user_input})

    global model
    model = AutoModelForCausalLM.from_pretrained(model_name_or_path, device_map="auto", torch_dtype=torch.float16, quantization_config = BitsAndBytesConfig(load_in_8bit=True), attn_implementation="flash_attention_2")
    res=generate_response()
    del model
    gc.collect()
    torch.cuda.empty_cache()

    return(res)

def on_release(key):
    global talk
    if(key==Key.page_up):
        talk=False
        stream.stop()
    if(key==Key.page_down):
        talk=False
        stream.stop()
        message(input(overwrite="True"))
        app.update_text()
    return

def print(text: str):
    if(text_mode):
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
    if(text_mode and not overwrite):
        return(builtins.input(prompt))

    print(prompt)
    
    with AudioToTextRecorder(model="tiny.en", language="en", post_speech_silence_duration=1) as recorder:
        with contextlib.redirect_stdout(None):
            text=recorder.text()
        builtins.print("\033[1m\033[92m⚡ synthesizing\033[0m → \'"+text+"\'")
        return(text)

def try_parse_tool_calls(content: str):
    """Try parse the tool calls."""
    tool_calls = []
    offset = 0
    for i, m in enumerate(re.finditer(r"<tool_call>\n(.+)?\n</tool_call>", content)):
        if i == 0:
            offset = m.start()
        try:
            func = json.loads(m.group(1))
            tool_calls.append({"type": "function", "function": func})
            if isinstance(func["arguments"], str):
                func["arguments"] = json.loads(func["arguments"])
        except json.JSONDecodeError as e:
            print(f"Failed to parse tool calls: the content is {m.group(1)} and {e}")
            pass
    if tool_calls:
        if offset > 0 and content[:offset].strip():
            c = content[:offset]
        else: 
            c = ""
        return {"role": "assistant", "content": c, "tool_calls": tool_calls}
    return {"role": "assistant", "content": re.sub(r"<\|im_end\|>$", "", content)}


def run_console_command(command: str) -> dict:
    command=command.replace('\\n', '\n').replace('\\t', '\t').replace('\\','')
    terminal_width = shutil.get_terminal_size().columns
    builtins.print("\n" + "=" * terminal_width+"\n")
    time.sleep(1)
    e=-2
    while(e==-2):
        messages_eval = [
            {
                "role": "system",
                "content": (
                    "You are an assistant that interprets linux console commands. "
                    "When prompted with a command, state accurately and truthfully, what that command does. "
                    "Keep your response brief but include all relevant information. "
                ),
            }
        ]
        messages_eval.append({"role": "user", "content": command})
        with Spinner("Interpreting..."):
            text = tokenizer.apply_chat_template(messages_eval, add_generation_prompt=True, tokenize=False)
            inputs = tokenizer(text, return_tensors="pt").to(model.device)
            outputs = model.generate(**inputs, max_new_tokens=512)
            response = tokenizer.batch_decode(outputs)[0][len(text):]
            response = re.sub(r"<\|im_end\|>$", "", response)
        if askyesno("Confirm command execution", command+"\n\n"+response):
            e=1
        else:
            e=0       
    if(e==1):
        print("Executing command: "+command+"\n")
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = p.communicate()
        if p.returncode != 0:
            builtins.print("\n"+"-" * terminal_width+"\n")
            print("Error calling command: "+error.decode())
            builtins.print("=" * terminal_width + "\n")
            return {
                "command": command, "output": error.decode(), "status": "failed"
            }
        else:
            builtins.print("\n"+"-" * terminal_width+"\n")
            if(output.decode()=="" and error.decode()!=""):
                builtins.print(error.decode())
            else:
                builtins.print(output.decode())
            builtins.print("=" * terminal_width + "\n")
            if(output.decode()=="" and error.decode()!=""):
                return {"command": command, "output": error.decode(), "status": "error"}
            else:
                return {"command": command, "output": output.decode(), "status": "success"}
    elif(e==0):
        builtins.print("\n"+"-" * terminal_width+"\n")
        print("Command denied by user")
        builtins.print("=" * terminal_width + "\n")
        return {
            "command": command, "output": "command denied by user", "status": "denied"
        }

def fetch_wikipedia_content(search_query: str) -> dict:
    """Fetches wikipedia content for a given search_query"""
    print("Fetching wikipedia content for "+search_query)
    try:
        # Search for most relevant article
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": search_query,
            "srlimit": 1,
        }

        url = f"{search_url}?{urllib.parse.urlencode(search_params)}"
        with urllib.request.urlopen(url) as response:
            search_data = json.loads(response.read().decode())

        if not search_data["query"]["search"]:
            return {
                "status": "error",
                "message": f"No Wikipedia article found for '{search_query}'",
            }

        # Get the normalized title from search results
        normalized_title = search_data["query"]["search"][0]["title"]

        # Now fetch the actual content with the normalized title
        content_params = {
            "action": "query",
            "format": "json",
            "titles": normalized_title,
            "prop": "extracts",
            "exintro": "true",
            "explaintext": "true",
            "redirects": 1,
        }

        url = f"{search_url}?{urllib.parse.urlencode(content_params)}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        pages = data["query"]["pages"]
        page_id = list(pages.keys())[0]

        if page_id == "-1":
            return {
                "status": "error",
                "message": f"No Wikipempg123 /usr/share/sounds/ubuntu/stereo/positive-acknowledge.wavdia article found for '{search_query}'",
            }

        content = pages[page_id]["extract"].strip()
        return {
            "status": "success",
            "content": content,
            "title": pages[page_id]["title"],
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_between(s:str, start:str, end:str) -> str:
    s=s[s.find(start)+len(start):]
    return(s[:s.find(end)])

def remove_between(s:str, start:str, end:str) -> str:
    o=""
    w=True
    for c in s:
        if(c in start):
            w=False
        elif(c in end):
            w=True
            o+=" "
        elif(w):
            o+=c
    return(o)

def unempty(s:str) -> str:
    o=""
    for line in s.splitlines():
        if len(set(line) & alnum) > 0:
            o+=line+"\n"
    return(o)

def fetch_website(query:str) -> dict:
    print("Getting page for "+query)

    url=serp.search(q=query, engine="google", hl="en", gl="us")["organic_results"][0]["link"]
    
    try:
        fp = urllib.request.urlopen(url.replace(" ","_"))
        mybytes = fp.read()
        page_source = mybytes.decode("utf8")
        head=get_between(page_source,"<title>","</title>")
        body=get_between(page_source,"<body>","</body>")
        body=unempty(body)
        body=body.replace('\\"','~dnr~')
        body=body.replace('</tr>','~nl~')
        body=body.replace('<br>','~nl~')
        body=remove_between(body,'<{"','}>"')
        body=body.replace('~dnr~','"')
        body=' '.join(body.split())
        body=body.replace('.','.\n')
        body=unempty(body)
        with open("./source.html","w") as f:
            f.write("Head:\n")
            f.write(head)
            f.write("\nBody\n")
            f.write(body)
        
        resp={"status": "success","query": query, "page_url": url, "page_title": head, "page_body": body}
        
        return (resp)
    except Exception as e:
        # Close the WebDriver
        print(e)
        return {"status": "error", "message": str(e)}
        
def type_text(text:str) -> dict:

    print("Typing: "+text)
    
    pyautogui.typewrite(text)

    resp={"status": "success"}
    return (resp)
# Define tool for LM Studio
CONSOLE_TOOL = {
    "type": "function",
    "function": {
        "name": "run_console_command",
        "description": (
            "Run a command generated by you in the linux console. "
            "Always use this if the user is asking for an action, that you normally cannot perform. "
            "Never use this to access information from the internet or wikipedia. "
            "If the result is an error, correct the command and try again."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The linux console command, you want to execute",
                },
            },
            "required": ["command"],
        },
    },
}

WIKI_TOOL = {
    "type": "function",
    "function": {
        "name": "fetch_wikipedia_content",
        "description": (
            "Search Wikipedia and fetch the introduction of the most relevant article. "
            "Always use this if the user is asking for information that is likely on wikipedia. "
            "If the user has a typo in their search query, correct it before searching."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "Search query for finding the Wikipedia article",
                },
            },
            "required": ["search_query"],
        },
    },
}

WEB_TOOL = {
    "type": "function",
    "function": {
        "name": "fetch_website",
        "description": (
            "Returns the text content of the first website for a given search query. "
            "Always use this if the user is asking for information that is likely on websites other than wikipedia. "
            "If the user has a typo in their search query, correct it before searching."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to get information about",
                },
            },
            "required": ["query"],
        },
    },
}

TEXT_TOOL = {
    "type": "function",
    "function": {
        "name": "type_text",
        "description": (
            "Controls the users keyboard to type a provided text into a text field. "
            "Use this functin, if the user asks you to type down or write down a text. "
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to type",
                },
            },
            "required": ["text"],
        },
    },
}

# Class for displaying the state of model processing
class Spinner:
    def __init__(self, message="Processing..."):
        self.spinner = itertools.cycle(["-", "/", "|", "\\"])
        self.busy = False
        self.delay = 0.1
        self.message = message
        self.thread = None

    def write(self, text):
        sys.stdout.write(text)
        sys.stdout.flush()

    def _spin(self):
        while self.busy:
            self.write(f"\r{self.message} {next(self.spinner)}")
            time.sleep(self.delay)
        self.write("\r\033[K")  # Clear the line

    def __enter__(self):
        self.busy = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.busy = False
        time.sleep(self.delay)
        if self.thread:
            self.thread.join()
        self.write("\r")  # Move cursor to beginning of line

def get_function_by_name(fn_name):
    if(fn_name=="run_console_command"):
        return run_console_command
    elif(fn_name=="fetch_wikipedia_content"):
        return fetch_wikipedia_content
    elif(fn_name=="fetch_website"):
        return fetch_website
    elif(fn_name=="type_text"):
        return type_text

def call_tools(fn_name, fn_args):

        args = fn_args

        result = get_function_by_name(fn_name)(**args)

        # Print the Wikipedia content in a formatted way
        if result["status"] == "success":
            print("tool-call OK\n")
        else:
            print("tool-call FAILED\n")

        messages.append(
            {
                "role": "tool",
                "content": json.dumps(result),
                "name": fn_name,
            }
        )

def generate_response():

    if(short_answer):
        messages_a=messages+[{"role": "system", "content": "Answer as a friendly and cute woman. Answer short and precise."}]
    else:
        messages_a=messages+[{"role": "system", "content": "Answer as a friendly and cute woman. Answer precisely."}]

    if(webtool):
        tools=[CONSOLE_TOOL,WIKI_TOOL,WEB_TOOL,TEXT_TOOL]
    else:
        tools=[CONSOLE_TOOL,WIKI_TOOL,TEXT_TOOL]
    try:
        with Spinner("Thinking..."):
            text = tokenizer.apply_chat_template(messages_a, tools=tools, add_generation_prompt=True, tokenize=False)
            inputs = tokenizer(text, return_tensors="pt").to(model.device)
            outputs = model.generate(**inputs, max_new_tokens=512)
            response = tokenizer.batch_decode(outputs)[0][len(text):]
            messages.append(try_parse_tool_calls(response))

        if tool_calls := messages[-1].get("tool_calls", None):
            # Handle all tool calls
            for tool_call in tool_calls:
                if fn_call := tool_call.get("function"):
                    fn_name: str = fn_call["name"]
                    fn_args: dict = fn_call["arguments"]
                    call_tools(fn_name,fn_args)

            # Stream the post-tool-call response
            return(generate_response())
            
        else:
            # Handle regular response
            message=messages[-1].get("content")
            print(message)
            return(message)

    except Exception as e:
        print(
            f"\nError chatting with the LM Studio server!\n\n"
            f"Error details: {str(e)}\n"
        )
        return(f"ERROR: {str(e)}")

class App(tk.Tk):
    def __init__(self):
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

        self.listen = tk.Button(text="LISTEN", bd=0)
        self.listen.bind("<Button-1>", self.handle_listen)
        self.listen.grid(row=2, column=3, pady=5, padx=5)

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
        if(listen):
            self.listen.config(background="green")
        else:
            self.listen.config(background="gray")
        if(short_answer):
            self.short.config(background="green")
        else:
            self.short.config(background="gray")
        if(text_mode):
            self.mode_d.config(text="TEXT")
        else:
            self.mode_d.config(text="VOICE")

    def update_text(self):
        self.log.delete(1.0,tk.END)
        for message in messages:
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
        r=message(inp)
        if("ERROR:" in r):
            self.log.insert(tk.END, r+"\n", 'system')
            self.log.see(tk.END)
        else:
            self.update_text()
        if(exit):
            self.destroy()
        self.submit.config(background="gray")

    def handle_listen(self, event):
        global listen
        listen=not listen
        global text_mode
        global tmp
        if(listen):
            tmp=text_mode
            text_mode=False
        else:
            text_mode=tmp
        self.get_state()

    def handle_voice(self, event):
        self.voice.config(background="red")
        inp=input(overwrite=True)
        self.log.insert(tk.END, "You: "+inp+"\n", 'user')
        self.log.insert(tk.END, "Nova: THINKING...\n", 'nova')
        self.log.see(tk.END)
        self.update()
        r=message(inp)
        if("ERROR:" in r):
            self.log.insert(tk.END, r+"\n", 'system')
            self.log.see(tk.END)
        else:
            self.update_text()
        if(exit):
            self.destroy()
        self.voice.config(background="gray")

    def handle_mode(self, event):
        global text_mode
        text_mode=not text_mode
        self.get_state()

    def handle_short(self, event):
        global short_answer
        short_answer=not short_answer
        self.get_state()

    def handle_save(self, event):
        file_path="./"+self.path.get()+".bin"
        print("\nSaving chat-log to "+file_path)
        with open(file_path, 'wb') as file:
            pickle.dump(messages, file)

    def handle_load(self, event):
        file_path="./"+self.path.get()+".bin"
        try:
            print("\nLoading chat-log from "+file_path)
            with open(file_path, 'rb') as file:
                messages[:] = pickle.load(file) + messages
            self.update_text()
        except FileNotFoundError:
            print("\nFailed loading chat-log from "+file_path)

    def handle_clear(self, event):
        del messages[:]
        messages[:]=primer
        self.update_text()

    def on_closing(self):
        global exit
        exit=True
        self.destroy()

def run_tkinter_app():
    """Function to start and manage the Tkinter application."""
    global app
    app = App()
    app.mainloop()

def async_task():
    global app
    while not exit:
        time.sleep(0.1)
        
        if(listen):
            message(input())
            app.update_text()

def chat_loop():
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

