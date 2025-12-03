#!/usr/bin/env python3
import subprocess
import sys
import os
import shutil
from datetime import datetime
from jinja2 import Template

# === BASE PATHS (relative al repo) ===
THIS_FILE = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(THIS_FILE))        # ../  from scripts/
DEFAULT_TEMPLATES = os.path.join(REPO_ROOT, "templates")
DEFAULT_LOGDIR = os.path.join(REPO_ROOT, "logs_html")

LOG_DIR = os.environ.get("LOGVIEWER_DIR", DEFAULT_LOGDIR)
TEMPLATE_DIR = os.environ.get("TEMPLATE_DIR", DEFAULT_TEMPLATES)
TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "log_template.html")

os.makedirs(LOG_DIR, exist_ok=True)

# === INPUT ===
if len(sys.argv) < 2:
    print("❌ Uso: log_to_html.py <comando | file.log>")
    sys.exit(2)

target = sys.argv[1]
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# === DETERMINA MODE, CMD e BASE_NAME ===
if os.path.isfile(target) and target.endswith(".log"):
    mode = "file"
    base_name = os.path.basename(target).replace(".", "_")
    cmd = f"Visualizzazione log: {target}"
else:
    mode = "command"
    # unisci tutti gli argomenti (mantieni eventuali spazi)
    cmd = " ".join(sys.argv[1:])
    base_name = cmd.split()[0].replace("/", "_").replace(".", "_").replace(" ", "_")

filename = f"{base_name}_{timestamp}.html"
filepath = os.path.join(LOG_DIR, filename)

# === ESECUZIONE / LETTURA ===
try:
    if mode == "file":
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            output = f.read()
    else:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        output = (result.stdout or "") + (result.stderr or "")
except Exception as e:
    output = f"❌ Errore durante l'esecuzione: {e}"

print(f"\n📤 Output ({mode}):\n{'-'*40}\n{output}\n{'-'*40}")

# === CARICA TEMPLATE (verifica esistenza) ===
if not os.path.exists(TEMPLATE_PATH):
    print(f"❌ Template non trovato: {TEMPLATE_PATH}")
    print("   Controlla TEMPLATE_DIR o imposta TEMPLATE_DIR env var al path del template.")
    sys.exit(3)

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = Template(f.read())

html = template.render(
    title=f"{base_name} – {timestamp}",
    base_name=base_name,
    timestamp=timestamp,
    cmd=cmd,
    output=output,
    filename=filename
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(html)

# === SINCRONIZZA ASSET (style.css, theme.js) dalla TEMPLATE_DIR alla LOG_DIR ===
for asset in ("style.css", "theme.js"):
    src = os.path.join(TEMPLATE_DIR, asset)
    dst = os.path.join(LOG_DIR, asset)
    try:
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy(src, dst)
    except Exception as e:
        print(f"⚠️ Impossibile copiare asset {asset}: {e}")

# === APERTURA AUTOMATICA (silenziosa in caso di errore) ===
# try:
#     subprocess.run(["xdg-open", filepath], check=False)
# except Exception:
#     pass

print(f"✅ Log HTML salvato in: {filepath}")
