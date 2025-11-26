#!/bin/bash

# === CONFIGURAZIONE ===
LOG_DIR="${LOGVIEWER_DIR:-$HOME/logviewer/logs_html}"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
CMD="$*"
FILENAME="log_${TIMESTAMP}.html"

# === VERIFICA CARTELLA DESTINAZIONE ===
mkdir -p "$LOG_DIR"

# === ESECUZIONE COMANDO E SALVATAGGIO IN HTML ===
{
  echo "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Log $TIMESTAMP</title>"
  echo "<style>body{font-family:monospace;white-space:pre-wrap;background:#f9f9f9;padding:1em;}</style></head><body>"
  echo "<h2>🧾 Comando:</h2><pre><code>$CMD</code></pre>"
  echo "<h2>📤 Output:</h2><pre><code>"
  eval "$CMD" 2>&1
  echo "</code></pre></body></html>"
} > "$LOG_DIR/$FILENAME"

# === FEEDBACK ===
echo "✅ Output salvato in: $LOG_DIR/$FILENAME"
