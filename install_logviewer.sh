#!/bin/bash
# install_logviewer.sh - installer per Logviewer

TARGET_DIR="$HOME/docker-stacks/logviewer"
BASH_PROFILE="$HOME/.bash_profile"
BASHRC="$HOME/.bashrc"
HELPER_FILE="$HOME/.logviewer_aliases"

# 1. Clona il repository se non esiste
if [ ! -d "$TARGET_DIR/.git" ]; then
  echo "Clono logviewer in $TARGET_DIR..."
  git clone https://github.com/robertozz/logviewer.git "$TARGET_DIR"
else
  echo "Repository già presente in $TARGET_DIR"
fi

# 2. Aggiungi descrizione in bash_profile (se non già presente)
if ! grep -q "Logviewer" "$BASH_PROFILE" 2>/dev/null; then
  cat >> "$BASH_PROFILE" <<'EOF'

echo ""
echo -e "${BRed}Logviewer${Color_Off} - visualizzatore log via Flask/Docker"
echo -e " ${UGreen}Installazione:${Color_Off} git clone https://github.com/robertozz/logviewer.git ~/docker-stacks/logviewer"
echo -e " ${UGreen}Avvio:${Color_Off} logviewer start"
echo -e " ${UGreen}Stop:${Color_Off} logviewer stop"
echo -e " ${UGreen}Restart:${Color_Off} logviewer restart"
echo -e " ${UGreen}Status:${Color_Off} logviewer status"
echo -e " ${UGreen}genlog:${Color_Off} logviewer genlog <command>"
echo ""

EOF
  echo "Descrizione aggiunta a $BASH_PROFILE"
else
  echo "Descrizione già presente in $BASH_PROFILE"
fi

# 3. Prepara file helper con i comandi logviewer
cat > "$HELPER_FILE" <<'EOF'
# Funzione logviewer: install|start|stop|restart|status|genlog
logviewer() {
  case "$1" in
    install)
      git clone https://github.com/robertozz/logviewer.git ~/docker-stacks/logviewer && echo "Clonato in ~/docker-stacks/logviewer"
      ;;
    start)
      (cd ~/docker-stacks/logviewer && sudo docker compose up -d --build) || (cd ~/docker-stacks/logviewer && nohup python3 app.py &)
      ;;
    stop)
      (cd ~/docker-stacks/logviewer && sudo docker compose down) || pkill -f "app.py" || true
      ;;
    restart)
      (cd ~/docker-stacks/logviewer && sudo docker compose down && sudo docker compose up -d --build) || (pkill -f "app.py" || true; nohup python3 ~/docker-stacks/logviewer/app.py &)
      ;;
    status)
      (cd ~/docker-stacks/logviewer && sudo docker compose ps) || pgrep -af "app.py" || echo "Non in esecuzione"
      ;;
    genlog)
      # scorciatoia per generare un log HTML da remoto
      # esempio: logviewer genlog /var/log/syslog
      if [ -z "$2" ]; then
        echo "Usage: logviewer genlog <file>"
      else
        (cd ~/docker-stacks/logviewer/scripts && python3 log_to_html.py "$2")
        echo "Log convertito in HTML, visibile via interfaccia web"
      fi
      ;;
    *)
      echo "Usage: logviewer {install|start|stop|restart|status|genlog}"
      ;;
  esac
}
EOF

# 4. Integra helper file in bashrc (se non già presente)
if ! grep -q ".logviewer_aliases" "$BASHRC" 2>/dev/null; then
  echo "source $HELPER_FILE" >> "$BASHRC"
  echo "Richiamo a $HELPER_FILE aggiunto in $BASHRC"
else
  echo "Richiamo già presente in $BASHRC"
fi

echo "Installazione completata. Ricarica con: source ~/.bashrc && source ~/.bash_profile"
