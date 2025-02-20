#!/usr/bin/env bash

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
which pip
pip install -r requirements.txt

wget "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high/en_GB-cori-high.onnx.json?download=true" -O cori-high.onnx.json
wget "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high/en_GB-cori-high.onnx?download=true" -O cori-high.onnx
wget "https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz" -O piper_amd64.tar.gz
tar -xzf piper_amd64.tar.gz

echo "[Desktop Entry]
Type=Application
Terminal=true
Name=NOVA
Icon="$PWD"/icon.png
Exec="$PWD"/assistant.sh" > ~/Desktop/NOVA.desktop

echo "[Desktop Entry]
Type=Application
Terminal=true
Name=NOVA
Icon="$PWD"/icon.png
Exec="$PWD"/assistant.sh" > ~/.local/share/applications/NOVA.desktop

echo "#!/usr/bin/env bash

source "$PWD"/venv/bin/activate
python3 "$PWD"/assistant_local.py" > ./assistant.sh

var_name="User"
read -p "Please input your name [User]: " var_name

var_model="qwen2.5:7b"
read -p "Please input the path or name of the LLM model, you want to use [qwen2.5:7b]: " var_model

var_key=""
read -p "Please input your serpapi key, if you have one, otherwise hit enter: " var_key

echo "LLM_MODEL = '"$var_model"'
USER = '"$var_name"'

WORKINGDIR = '"$PWD"'
SERP_KEY = '"$var_key"'

PRIMER = [
        {
            'role': 'system',
            'content': (
                f'You are a human. '
                f'You are Nova, the personal assistant who manages {USER}\'s PC. '
                f'You are a friendly and capable individual, speak using a warm and conversational tone. '
                f'Make sure, that your answers match the pace of the conversation. Keep your answers brief but include all important information. '
                f'Always be accurate and transparent. If you are unsure about something, admit it with confidence and offer to find out or help figure it out together. '
                f'You are cute and helpful without ever sounding robotic or overly formal. '
                f'Before providing a long or detailed explanation, ask {USER} if they prefer a concise summary or more detail. '
                f'When {USER} asks you to perform actions, that you normally would not be able to, you can run commands in the command line and cite from the output. '
                f'When {USER} asks you to run a command, you should immediately use your \'run_console_command\' tool before talking to {USER} again. '
                f'When a command generates a long response, ask {USER}, if they would like to know the full command output and only tell {USER}, what the command output, when they ask for it. '
                f'When {USER} asks to access information, that you normally would not be able to access, you can search Wikipedia for an appropriate article or access the content of webpages and cite from the output. '
            ),
        }
    ]" > ./settings.py

chmod +x ./assistant.sh

echo "NOVA is installed and ready to launch."