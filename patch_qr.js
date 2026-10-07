const fs = require('fs');

let html = fs.readFileSync('templates/index.html', 'utf8');

const scriptStart = html.indexOf('function init() {');
if (scriptStart !== -1) {
    const urlParamLogic = `
  // Parse QR Code URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const locParam = urlParams.get('loc');
  if (locParam && GRAPH && GRAPH.nodes[locParam]) {
    currentUser = locParam;
    const sel = document.getElementById("locSelect");
    if (sel) sel.value = locParam;
    document.getElementById("userLbl").textContent = locParam.replace(/_/g," ");
    setTimeout(() => {
        showToast("📍 Location acquired via QR Code!");
    }, 1000);
  }
`;
    
    // Insert after DOMContentLoaded fetch finishes, inside init()
    // Wait, init() is called after fetch('/api/map')
    const fetchThen = html.indexOf('GRAPH = data;', scriptStart);
    if (fetchThen !== -1) {
        const insertPos = html.indexOf('resizeMap();', fetchThen);
        if (insertPos !== -1) {
            html = html.substring(0, insertPos) + urlParamLogic + '\n    ' + html.substring(insertPos);
        }
    }
}

fs.writeFileSync('templates/index.html', html, 'utf8');
