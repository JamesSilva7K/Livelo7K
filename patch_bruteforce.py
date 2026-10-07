from pathlib import Path

app_file = Path("app.py")
content = app_file.read_text("utf-8")

if "failed_attempts = {}" not in content:
    bruteforce_logic = """
import time
failed_attempts = {}

def is_blocked(ip):
    data = failed_attempts.get(ip)
    if not data: return False
    if data['count'] >= 5:
        if time.time() - data['last'] < 300: # 5 minutes block
            return True
        else:
            del failed_attempts[ip]
    return False

def record_auth_fail(ip):
    data = failed_attempts.get(ip, {'count': 0, 'last': 0})
    data['count'] += 1
    data['last'] = time.time()
    failed_attempts[ip] = data

def reset_auth_fail(ip):
    if ip in failed_attempts:
        del failed_attempts[ip]
"""
    content = content.replace("import os", "import os\n" + bruteforce_logic)
    app_file.write_text(content, "utf-8")
    print("Bruteforce logic added to app.py")
