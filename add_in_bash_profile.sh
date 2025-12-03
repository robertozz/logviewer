grep -q "logviewer() {" ~/.bash_profile 2>/dev/null || cat >> ~/.bash_profile <<'EOF'
# helper per logviewer: install|start|stop|restart|status
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
    *)
      echo "Usage: logviewer {install|start|stop|restart|status}"
      ;;
  esac
}
EOF
source ~/.bash_profile
