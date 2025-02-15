#!/usr/bin/env bash

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