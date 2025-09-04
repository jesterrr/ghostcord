# THE AUTHOR IS NOT RESPONSIBLE FOR ANY MISUSE OR DAMAGES, PROJECT WAS MADE FOR EDUCATIONAL AND AUTHORIZED RESEARCH USE ONLY!!!!

# GC - GhostCord

GhostCord is a Discord based C2 agent that uses discord bot for control.

# How it works

The c2 agent is a discord bot which will run on the device that the owner wants to control. This way, there is no p2p connection. The c2 agent connects itself to a discord bot , which is then controlled in a discord server using commands.

The diagram:

![Diagram](https://github.com/jesterrr/ghostcord/blob/main/diagram.png)

## How To Install

### 1. Clone the Repository
```bash
git clone https://github.com/jesterrr/ghostcord.git
cd ghostcord/
```

### 2. Instal requirements (VERY IMPORTANT)
```bash
pip install -r requirements.txt
```

### 3. Prepare the Agent Template
- The agent template is `agent_template.py`.
- It uses  `{BOT_TOKEN}`, `{CHANNEL_ID}`, `{OWNER_ID}` for configuration.
- If you want, tweak and change stuff in the template.

### 4. Build Your Agent
Run the builder and follow the prompts:
```bash
python builder.py
```
- This will generate a file named `c2.py` with the configs  

### 4.5 (OPTIONAL) Convert the .py file to .exe / Obfuscate the code

You can use any of the converters or obfuscators to do it.

### 5. Run the Agent on the device
```bash
python c2.py
```

## Optional 
Some features require extra Python packages:
- `pyautogui` (screenshots, automation)
- `psutil` (system/process info)
- `pyperclip` (clipboard)
- `cv2` (webcam)
- `pyttsx3` (text-to-speech)
- `requests` (network, file upload)

Install them if needed:
```bash
pip install pyautogui psutil pyperclip opencv-python pyttsx3 requests
```


