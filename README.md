## Security & Disclaimer
- **For educational and authorized research use only.**
- **The author is NOT responsible for misuse or damages.**

# Ghostcord

Discord-Bot based C2 agent

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
- It uses placeholders `{BOT_TOKEN}`, `{CHANNEL_ID}`, `{OWNER_ID}` for configuration.
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

## Config
- **BOT_TOKEN**: Your Discord bot token.
- **CHANNEL_ID**: The Discord channel ID.
- **OWNER_ID**: Your Discord user ID. 

## Optional Dependencies
Some features require extra Python packages:
- `pyautogui` (screenshots, automation)
- `psutil` (system/process info)
- `pyperclip` (clipboard)
- `cv2` (webcam)
- `pyttsx3` (text-to-speech)
- `requests` (network, file upload)

Install them as needed:
```bash
pip install pyautogui psutil pyperclip opencv-python pyttsx3 requests
```

