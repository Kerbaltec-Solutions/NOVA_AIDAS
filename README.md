# Nova-AIDAS (Nova-Artificial Intelligence Diagnosis and Assistance System)

Nova-AIDAS is based on Qwen2.5-Instruct and is designed to run console commands and look up information from the internet. 
Nova operates entirely locally and does not send any data to third-party servers unless you choose to access the internet. 
It unloads the model from the GPU when not in use to allow for background use. 
When attempting to run a console command, a separate instance will evaluate the command, and the user is prompted to decide if the command should be executed. (Read more in the AI safety section)

## Dependencies

Nova is designed to work on Linux-based shells. The following dependencies are required:

- Python 3
- Ollama (installed automatically during setup)

All necessary Python packages should be automatically installed into a virtual environment. If you encounter any issues, please open an issue.

The current setup uses a 7B parameter model. If you have a GPU with less VRAM, you might want to use the 3B Qwen model. This can be configured in the Python script. If you have a GPU with more VRAM, you might want to use the 14B Qwen model. This can also be configured in the Python script.

## Setup

1. Download all files and unpack them in a suitable location. 
   - `git clone https://github.com/Kerbaltec-Solutions/NOVA_AIDAS.git`
2. Move into the `NOVA_AIDAS` folder  
   - `cd NOVA_AIDAS`
3. If you would like Nova to have the ability to search the web beyond just Wikipedia, create on at their Webpage and add it during setup. 
4. Inside the "NOVA_AIDAS" folder, run the `setup.sh` file. This will create a desktop shortcut and a launch file.
   - `./setup.sh`
5. You can now start the assistant via the `assistant.sh` file or the desktop shortcut.
   - `./assistant.sh`

## Usage

After starting the program, two windows will open: a console window for debugging and a main window. (Give it a few seconds)

In the main window, you will find (from top to bottom, left to right):

- **Chat Window**: Shows the past chat. Do not type in here.
- **Input Window**: Type your message here (Confirm with ENTER).
- **Submit Button**: Submit your message (alternative to ENTER).
- **Mode Button**: Switch between text-only and TTS output.
- **Short Button**: Adds extra commands to the AI to keep messages short. Good for conversational use; disable if you want detailed explanations.
- **Listen Button**: Set the AI to continuously listen for user voice input.
- **Voice Button**: Single-shot voice input.
- **Load Button**: Load chat log from the defined log file.
- **Save Button**: Save chat log to the defined log file.
- **Log File Name Input**: Name of the log file to save/load to/from.
- **Clear Button**: Wipes chat to remove all context from the AI.

**Notes**:
- When in voice mode, the chat window will only update after the voice output has completed.
- You can also use a middle mouse button click on the main window to activate single-shot voice input.
- The program will listen to the "Page-Up" key to shut down the voice output immediately and the "Page-Down" key to activate single-shot voice input. This works in the background too.

## AI Safety

This program is distributed as open source. As such, I do not have any influence on what you do with it. However, to avoid the "AI-Apocalypse," you should keep certain safeguards in place. In this program, the AI cannot execute any console command without the user's permission. This prevents the AI from performing any action in the real world. Always double-check if the command should be run and ensure it poses no risk.

