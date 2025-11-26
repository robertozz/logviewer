<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>Log Viewer</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='bootstrap.min.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <div class="container py-4">
    <div class="toolbar mb-3 d-flex justify-content-between align-items-center">
      <div>
        <button onclick="toggleTheme()" id="themeToggle">🌙 Tema: Scuro</button>
        <button onclick="location.reload()">🔄 Aggiorna lista</button>
      </div>
      <div class="d-flex align-items-center">
        <input type="text" id="searchInput" class="form-control form-control-sm me-2"
               placeholder="🔍 Cerca..." onkeyup="filterItems()">
        <a href="/logs.zip" class="btn btn-sm btn-outline-primary">⬇️ Scarica tutti i log</a>
      </div>
    </div>

    <h1 class="mb-4">📄 Log Viewer</h1>

    <h3>Log disponibili</h3>
    <ul class="list-group mb-4" id="logList">
      {% for file in logs %}
        <li class="list-group-item d-flex justify-content-between align-items-center">
          <a href="/log/{{ file }}" target="_blank">{{ file }}</a>
          <a href="/log/{{ file }}" download class="btn btn-sm btn-outline-primary">⬇️ Scarica</a>
        </li>
      {% endfor %}
    </ul>

    <h3>Script disponibili</h3>
    <ul class="list-group" id="scriptList">
      {% for file in scripts %}
        <li class="list-group-item d-flex justify-content-between align-items-center">
          <a href="/script/{{ file }}" target="_blank">{{ file }}</a>
          <a href="/script/{{ file }}" download class="btn btn-sm btn-outline-secondary">⬇️ Scarica</a>
        </li>
      {% endfor %}
    </ul>
  </div>

  <script src="{{ url_for('static', filename='theme.js') }}"></script>
  <script>
    function filterItems() {
      const input = document.getElementById("searchInput").value.toLowerCase();
      const lists = [document.querySelectorAll("#logList li"), document.querySelectorAll("#scriptList li")];
      lists.forEach(items => {
        items.forEach(li => {
          const text = li.textContent.toLowerCase();
          li.style.display = text.includes(input) ? "" : "none";
        });
      });
    }
  </script>
</body>
</html>
