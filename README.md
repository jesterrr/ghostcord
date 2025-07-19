# Ghostcord

Discord-Bot based Command and Control agent

## Security & Disclaimer
- **For educational and authorized research use only.**
- **The author is NOT responsible for misuse or damages.**

## Features
- Modular command system (shell, file, process, info, clipboard, etc.)
- Interactive builder for easy configuration
- Supports Windows, Linux (Feature set may vary)

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
- You can customize this template to add/remove features as needed.

### 4. Build Your Agent
Run the builder and follow the prompts:
```bash
python builder.py
```
- This will generate a ready-to-use `c2.py` with your configuration.

### 5. Run the Agent
```bash
python c2.py
```

## Configuration
- **BOT_TOKEN**: Your Discord bot token (from the Discord Developer Portal).
- **CHANNEL_ID**: The Discord channel ID where the agent will listen for commands.
- **OWNER_ID**: Your Discord user ID (only you can control the agent).

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

## Customization
- Edit `agent_template.py` to add/remove features or change behavior.
- The builder (`builder.py`) will always generate a fresh, configured agent for you.

