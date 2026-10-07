const fs = require('fs');

let html = fs.readFileSync('templates/index.html', 'utf8');

html = html.replace('.app { flex-direction: column; height: auto; overflow: visible; }', '.app { flex-direction: column-reverse; height: auto; overflow: visible; }');

fs.writeFileSync('templates/index.html', html, 'utf8');
