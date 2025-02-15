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
python3 "$PWD"/assistant_local.py "$PWD > ./assistant.sh

chmod +x ./assistant.sh

echo "NOVA is installed and ready to launch. 

Make shure to add assistant_serapi_key.txt, if you would like search capability"