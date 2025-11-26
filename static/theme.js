const themeToggle = document.getElementById("themeToggle");

function applyTheme(theme) {
  if (theme === "dark") {
    document.body.classList.add("dark");
    themeToggle.textContent = "☀️ Tema: Chiaro";
  } else {
    document.body.classList.remove("dark");
    themeToggle.textContent = "🌙 Tema: Scuro";
  }
}

function toggleTheme() {
  const isDark = document.body.classList.toggle("dark");
  const newTheme = isDark ? "dark" : "light";
  localStorage.setItem("theme", newTheme);
  applyTheme(newTheme);
}

const savedTheme = localStorage.getItem("theme") || "light";
applyTheme(savedTheme);

function copyOutput() {
  const text = document.getElementById("output").innerText;
  navigator.clipboard.writeText(text).then(() => alert("Output copiato!"));
}
