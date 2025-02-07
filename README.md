***Welcome to Nova-AIDAS (Nova-Artificial Intelligence Diagnosis and Assistance System)***

Nova is based upon Qwen2.5-Instruct and set up to run console commands and look up information from the internet. 
Nova runs entirely locally and will not send any data to third party servers (unless you want to access the internet)
Nova unloads the model from GPU when not in use to allow for background use.
When trying to run a console command, a sepperate instance will evaluate the command and the user is prompted to decide, if the command should be executed. (Read more in the AI safety section)

**Dependancies**

Nova is set up to work on Linux based shells. 

The python virtual environment is set up to work with CUDA 12.4. This has to be installed seperately. Additionally, Python3 is required.
All neccesary Python packages should be included in the venv and no additional installation should be required. Please open an issue, if it does not work.

The current setup is set to max out a Nvidia 3060 GPU. It is currently using a 3B parameter model. Lower parameter count models frequently struggle with tool calling.
If you have a GPU with more VRAM, you might want to try to use the 7B or 14B Qwen model. This can be set up in the Python script.

**Setup**

After downloading all files, unpack them in the place, where they can reside.
Then, inside the "NOVA_AIDAS" folder run the setup.sh file. This will create a desktop shortcut and a launchfile.
Also, you may want to open the assistant_local.py file and change the "USER" variable, to contain your name.
If you would like Nova to have the ability to search the web beyond just Wikipedia, you can create the file "assistant_serapi_key.txt" and insert your personal serapi key into it.
You can now start the assistant via the assistant.sh file or via the desktop shortcut.

**Useage**
After starting the program, two windows will open: A console window, which is there for debugging and a main window. (Give it some seconds)
In the main window, you will find (from top to bottom, left to right):
The chat window: Shows the past chat. Do not type in here.
The Input window: Type your message in here (Confirm with ENTER) 
Submit Button: Submit your message (alternative to ENTER)
Mode Button: Switch between Text only and TTS output
Short Button: Adds extra commands to the ai, in order to keep messages short. Good for conversational use, disable, if you want detailed explanations.
Listen Button: Set the AI to continuously listen for user voice input.
Voice Button: Single shot voice input.
Load Button: Load chatlog from defined log file
Save Button: Save chatlog to defined log file
Log file name input: Name of the log file to save/load to/from
Clear button: Wipes chat, to remove all context from the AI

Note: When in voice mode, the chat window will only update after the voice output has completed.
Note: You can also use a middle mouse button click on the main window to activate the single shot voice input.
Note: The programm will listen to the "Page-Up" key to shut down the voice output immediately and the "Page-Down" key to activate the single shot voice input. This works in the background too.

**AI safety**
This program is distributed as open source. As such i do not have any influence on what you do with it.
However, to avoid the "AI-Apocalypse", you should keep certain safeguards in order.
In the case of this program, this means, that the AI can not execute any console command without the user allowing it.
This disables the AI from performing any action in the real world. 
Allways double check, if the command should be run. Make shure, that it poses no risk.
