import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

js_add = """<script>
  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    const btn = document.getElementById('themeIcon');
    if (btn) btn.innerHTML = next === 'dark' ? '☀️' : '🌙';
    localStorage.setItem('admin-theme', next);
  }
  
  // Wait for DOM
  document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('admin-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const btn = document.getElementById('themeIcon');
    if (btn) btn.innerHTML = savedTheme === 'dark' ? '☀️' : '🌙';
  });

  let GRAPH=null"""

if "function toggleTheme" not in html:
    html = html.replace('<script>\n  let GRAPH=null', js_add)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
