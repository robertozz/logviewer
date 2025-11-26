# 🧭 LogViewer – Mini Server HTML per Log

LogViewer è un server leggero basato su Flask e Bootstrap, pensato per visualizzare file HTML generati da script di sistema, digest, e moduli di monitoraggio. È progettato per girare su Raspberry Pi in ambienti Dockerizzati.

## 📦 Funzionalità
- Visualizzazione log HTML in browser
- Interfaccia Bootstrap semplice e responsive
- Montaggio cartella `logs_html/` per output dinamico
- Compatibile con digest da `telegram_utils.py`, `ai-syshelper.sh`, ecc.

## 🚀 Avvio rapido
```bash
docker build --network=host -t logviewer .
docker run --rm -p 5000:5000 logviewer

## 📁 Struttura del progetto
~/logviewer/
├── app.py
├── Dockerfile
├── requirements.txt
├── scripts/
│   └── log_to_html.py
├── templates/
│   ├── log_template.html
│   ├── style.css
│   └── theme.js
├── logs_html/
│   ├── system_day.html
│   ├── wireguard_status.html
│   └── *.html
├── README.md

Log Viewer
Un semplice viewer web per file locali e symlink, progettato per essere eseguito in Docker. Mostra tre aree principali: log HTML (logs_html), script (scripts) e link generici (link_pool) — file o symlink con icona e descrizione basata sull’estensione.

Caratteristiche principali
Visualizzazione di tre sezioni: Log disponibili (HTML), Script disponibili (py/sh) e Link generici (qualsiasi estensione)

Mapping estensioni → icona e descrizione tramite ext_map.json (caricabile a runtime; fallback integrato)

Rilevamento symlink con visualizzazione di target raw e target risolto

Possibilità di servire symlink che puntano fuori dalla cartella montata tramite whitelist + bind mount controllati

Download singolo per file e download aggregato (ZIP) per tutti i log

Ricerca lato client e toggle tema nella UI

Struttura del repository
app.py — server Flask; costruisce le liste e fornisce le rotte:

/ — interfaccia principale

/log/<file> — serve file HTML dai log

/script/<file> — serve script

/link/<file> — serve file / risolve symlink (con whitelist)

/logs.zip — scarica tutti i log in zip

templates/index.html — template Jinja della UI

static/ — risorse statiche (CSS, JS, favicon)

logs_html/ — cartella bindata per log HTML

scripts/ — cartella bindata per script

link_pool/ — cartella bindata per file e symlink

ext_map.json — mapping estensioni → [emoji, label] (opzionale; fallback integrato in app.py)

ext_map.json (esempio)
Salva ext_map.json nella root del progetto (UTF-8). Modificalo per aggiungere/aggiornare icone e label.

json
{
  "txt": ["📄", "Testo"],
  "md": ["📄", "Markdown"],
  "log": ["📄", "Log"],
  "pdf": ["📕", "PDF"],
  "docx": ["📘", "Word"],
  "xlsx": ["📗", "Excel"],
  "pptx": ["📙", "PowerPoint"],
  "jpg": ["🖼️", "Immagine"],
  "jpeg": ["🖼️", "Immagine"],
  "png": ["🖼️", "Immagine"],
  "gif": ["🖼️", "Animazione"],
  "mp3": ["🎵", "Audio"],
  "mp4": ["🎞️", "Video"],
  "zip": ["🗜️", "Archivio"],
  "py": ["💻", "Python"],
  "sh": ["💻", "Shell"],
  "js": ["💻", "JavaScript"],
  "json": ["💻", "JSON"],
  "html": ["🌐", "HTML"],
  "": ["📦", "Sconosciuto"]
}
Esempio docker-compose (minimo)
Adatta i percorsi al tuo ambiente. Se vuoi servire symlink che puntano in /home/roberto/Downloads monta anche quella cartella (readonly consigliato).

yaml
version: "3.8"
services:
  logviewer:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./logs_html:/app/logs_html
      - ./scripts:/app/scripts
      - ./link_pool:/app/link_pool
      - ./templates:/app/templates
      - ./static:/app/static
      - ./ext_map.json:/app/ext_map.json:ro
      # Per servire target esterni (es. Downloads)
      # - /home/roberto/Downloads:/home/roberto/Downloads:ro
Avvio:

bash
sudo docker compose up -d --build
Per assicurarsi che le modifiche locali vengano viste dal container:

bash
sudo docker compose down
sudo docker compose up -d --build
sudo docker compose restart logviewer
Whitelist percorsi per symlink esterni
Per motivi di sicurezza la rotta /link/<file> permette di servire target esterni solo se:

Il target risolto è sotto una delle root definite in ALLOWED_TARGET_ROOTS in app.py.

La cartella che contiene il target è bind‑mountata nel container (es. /home/roberto/Downloads:/home/roberto/Downloads:ro).

Procedura:

Aggiungi il percorso assoluto alla lista ALLOWED_TARGET_ROOTS in app.py.

Aggiorna docker-compose.yml con il bind mount corrispondente (consigliato :ro).

Riavvia il container.

Non aggiungere root di sistema o cartelle sensibili alla whitelist.

Campi passati al template
Per ogni item app.py passa al template un dizionario con queste chiavi:

name — nome file

ext — estensione normalizzata (senza punto)

icon — emoji/icon associata all’estensione

type_label — descrizione testuale (es. "Immagine", "PDF")

is_symlink — booleano

target_raw / target_resolved — informazioni sul symlink (se presente)

Nel template usa {{ item.icon }}, {{ item.type_label }} e {{ item.name }}.

Comportamenti e limitazioni
Symlink relativi che puntano ancora dentro link_pool vengono serviti normalmente.

Symlink che puntano fuori sono serviti solo se il target è in whitelist e la cartella è montata nel container.

send_from_directory viene usato per file dentro le cartelle montate; send_file viene usato per target esterni consentiti.

I symlink mostrano il target raw e il target risolto; se il target non è accessibile il file ritornerà 404.

Per directory con molti file valuta caching o paginazione per evitare rallentamenti.

Troubleshooting rapido
Pagine vuote nella lista: assicurati che list_generic ritorni una lista di dict (non semplici stringhe).

"Not Found" su symlink esterni:

Verifica che il target sia montato nel container (docker exec -it logviewer ls -l /path/to/target).

Verifica che il percorso target sia aggiunto a ALLOWED_TARGET_ROOTS.

File host aggiornati non visibili: riavvia il container con --build.

"the input device is not a TTY" con here‑doc: usa docker exec -i o il comando inline con -c.

Miglioramenti possibili
Anteprima inline immagini (thumbnail nella lista)

Preview prime N righe per file di testo (.txt, .log, .md)

API JSON (/api/list) per integrazione con altri strumenti

Caching con invalidazione basata su timestamp file

Autenticazione e logging degli accessi per ambienti non locali

Contribuire
Fork del repository

Aggiungi/aggiorna ext_map.json se serve

Testa localmente (assicurati che i volumi siano montati correttamente)

Apri una Pull Request con descrizione delle modifiche

Licenza
MIT — sentiti libero di forkare, modificare e aprire PR.
