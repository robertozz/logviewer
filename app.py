"""
Log Viewer - avvio e riavvio

Esempi di riavvio:

# 1) Avvio diretto (sviluppo)
python3 app.py

# 2) Riavvio semplice (se lanciato in foreground)
# interrompi con CTRL+C e rilancia:
python3 app.py

# 3) Riavvio con systemd (esempio di unit file)
# sudo systemctl restart logviewer.service

# 4) Avvio/riavvio con Docker Compose (consigliato in produzione)
# dalla cartella del progetto:
# sudo docker compose up -d --build
# sudo docker compose down

# 5) Riavvio rapido (one-liner)
# pkill -f "app.py" || true && nohup python3 app.py &

Sostituisci i comandi con quelli adatti al tuo ambiente.
"""


from flask import Flask, render_template, send_from_directory, send_file, abort
import os
import json
import shutil
import re
from html import unescape

app = Flask(__name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(BASE_DIR, "logs_html")
SCRIPT_DIR = os.path.join(BASE_DIR, "scripts")
LINK_DIR = os.path.join(BASE_DIR, "link_pool")
EXT_MAP_PATH = os.path.join(BASE_DIR, "ext_map.json")

# Whitelist di percorsi esterni a cui è permesso servire file risolti dai symlink
ALLOWED_TARGET_ROOTS = [
    os.path.realpath(LINK_DIR),                 # la stessa link_pool
    os.path.realpath(BASE_DIR),                 # la cartella dell'app (opzionale)
    # aggiungi altre cartelle fidate se necessario, es:
    # os.path.realpath("/home/roberto/Downloads")
    # ma la devi aggiungere anche alle cartelle di docker-compose.yml
]

def load_ext_map(path=EXT_MAP_PATH):
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            return {k: (v[0], v[1]) for k, v in raw.items()}
    except Exception:
        # fallback minimale
        return {
            "": ("📦", "Sconosciuto"),
            "html": ("🌐", "HTML"),
            "txt": ("📄", "Testo"),
            "jpg": ("🖼️", "Immagine"),
            "jpeg": ("🖼️", "Immagine"),
            "png": ("🖼️", "Immagine"),
            "py": ("💻", "Python"),
            "sh": ("💻", "Shell"),
            "pdf": ("📕", "PDF"),
            "log": ("📄", "Log"),
            "md": ("📄", "Markdown"),
            "zip": ("🗜️", "Archivio")
        }

EXT_MAP = load_ext_map()

def ext_to_icon_and_label(ext):
    return EXT_MAP.get((ext or "").lower(), ("📦", ext or "Sconosciuto"))

def target_allowed(resolved_path):
    rp = os.path.realpath(resolved_path)
    for root in ALLOWED_TARGET_ROOTS:
        if os.path.commonpath([root, rp]) == root:
            return True
    return False

def _strip_tags(text):
    # rimuove tag HTML semplicemente
    return re.sub(r'<[^>]+>', '', text)

def extract_command_from_log(path):
    """
    Estrae il comando dal log HTML con più euristiche:
    1) commento HTML: <!-- command: ... -->
    2) meta tag: <meta name="command" content="...">
    3) <pre> o <code> che contengono comandi
    4) fallback: rimuove tag e cerca righe che iniziano con comandi tipici
    """
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
    except Exception:
        return None

    # 1) commento <!-- command: ... -->
    m = re.search(r'<!--\s*command\s*:\s*(.+?)\s*-->', html, flags=re.IGNORECASE | re.DOTALL)
    if m:
        return unescape(m.group(1).strip())

    # 2) meta tag <meta name="command" content="...">
    m = re.search(r'<meta[^>]*name=["\']command["\'][^>]*content=["\']([^"\']+)["\']', html, flags=re.IGNORECASE)
    if m:
        return unescape(m.group(1).strip())

    # 3) contenuto di <pre> o <code> (primo blocco che sembra un comando)
    for tag in ("pre", "code"):
        m = re.search(rf'<{tag}[^>]*>(.*?)</{tag}>', html, flags=re.IGNORECASE | re.DOTALL)
        if m:
            text = _strip_tags(m.group(1)).strip()
            # prendi la prima riga che sembra un comando
            for line in text.splitlines():
                line = line.strip()
                if re.match(r'^(cat |python |bash |sh |\.\/|/usr/|sudo )', line):
                    return unescape(line)

    # 4) fallback: rimuovi tag e cerca righe che iniziano con comandi tipici
    plain = _strip_tags(html)
    for line in plain.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r'^(command:)\s*(.+)', line, flags=re.IGNORECASE):
            return unescape(re.sub(r'^(command:)\s*', '', line, flags=re.IGNORECASE).strip())
        if re.match(r'^(cat |python |bash |sh |\.\/|/usr/|sudo )', line):
            return unescape(line)

    return None

def list_generic(path, exts=None):
    """
    Restituisce lista di dict con chiavi:
    name, ext, is_symlink, target_raw, target_resolved, icon, type_label, command
    """
    items = []
    try:
        names = sorted(os.listdir(path), reverse=True)
    except FileNotFoundError:
        names = []
    for name in names:
        if exts and not name.lower().endswith(exts):
            continue

        full = os.path.join(path, name)
        is_link = os.path.islink(full)
        target_raw = None
        target_resolved = None
        command = None

        if is_link:
            try:
                target_raw = os.readlink(full)
                target_resolved = os.path.realpath(
                    os.path.join(os.path.dirname(full), target_raw)
                )
            except OSError:
                target_raw = None
                target_resolved = None

        _, ext = os.path.splitext(name)
        ext = ext.lower().lstrip(".")
        icon, type_label = ext_to_icon_and_label(ext)

        # Se è un log HTML, prova a estrarre il comando
        if ext == "html":
            command = extract_command_from_log(full)

        items.append({
            "name": name,
            "ext": ext,
            "is_symlink": is_link,
            "target_raw": target_raw,
            "target_resolved": target_resolved,
            "icon": icon,
            "type_label": type_label,
            "command": command
        })
    return items

@app.route("/")
def index():
    logs = list_generic(LOG_DIR, exts=(".html",))
    scripts = list_generic(SCRIPT_DIR, exts=(".py", ".sh"))
    links = list_generic(LINK_DIR, exts=None)
    return render_template("index.html", logs=logs, scripts=scripts, links=links)

@app.route("/log/<path:filename>")
def serve_log(filename):
    if ".." in filename or filename.startswith("/"):
        abort(400)
    full = os.path.join(LOG_DIR, filename)
    if not os.path.exists(full):
        abort(404)
    # Serve direttamente: il template mostra il comando estratto nella lista principale
    return send_from_directory(LOG_DIR, filename)

@app.route("/script/<path:filename>")
def serve_script(filename):
    if ".." in filename or filename.startswith("/"):
        abort(400)
    return send_from_directory(SCRIPT_DIR, filename)

@app.route("/link/<path:filename>")
def serve_link(filename):
    if ".." in filename or filename.startswith("/"):
        abort(400)

    local_path = os.path.join(LINK_DIR, filename)
    if os.path.exists(local_path):
        # Symlink o file interno
        if os.path.islink(local_path):
            try:
                raw = os.readlink(local_path)
                target = os.path.realpath(os.path.join(os.path.dirname(local_path), raw))
            except OSError:
                abort(404)
            # Se il target risolto è ancora sotto LINK_DIR, servilo con send_from_directory
            if os.path.commonpath([os.path.realpath(LINK_DIR), target]) == os.path.realpath(LINK_DIR):
                rel = os.path.relpath(target, os.path.realpath(LINK_DIR))
                return send_from_directory(LINK_DIR, rel)
            # Se il target è esterno ma consentito, servilo con send_file
            if target_allowed(target) and os.path.exists(target):
                return send_file(target, as_attachment=False)
            # altrimenti non esporre il file
            abort(404)
        else:
            # file normale dentro link_pool
            return send_from_directory(LINK_DIR, filename)

    abort(404)

@app.route("/logs.zip")
def download_all():
    archive_path = "/tmp/logs"
    shutil.make_archive(archive_path, "zip", LOG_DIR)
    return send_from_directory("/tmp", "logs.zip", as_attachment=True)

if __name__ == "__main__":
    # Avvio server senza apertura automatica del browser
    app.run(host="0.0.0.0", port=5000, debug=True)
