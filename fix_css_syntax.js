const fs = require('fs');

let html = fs.readFileSync('templates/index.html', 'utf8');

// Find the start of the media query
const startIdx = html.indexOf('@media(max-width: 768px) {');
if (startIdx !== -1) {
    // We know exactly what the broken block looks like because we just saw it
    const brokenBlock = `@media(max-width: 768px) {
  body { height: auto; overflow-y: auto; }
  .app { flex-direction: column; height: auto; overflow: visible; }
  .map-col { min-height: 45vh; max-height: 45vh; flex: none; border-bottom: 2px solid var(--border); }
  .sidebar { 
    width: 100%; height: auto; border-right: none; 
    padding: 20px; box-shadow: none; border-radius: 0;
    overflow-y: visible;
  }
  .sidebar::before { display: none; }
}
  .app { flex-direction: column-reverse; }
}`;

    const cleanBlock = `@media(max-width: 768px) {
  body { height: auto; overflow-y: auto; }
  .app { flex-direction: column; height: auto; overflow: visible; }
  .map-col { min-height: 45vh; max-height: 45vh; flex: none; border-bottom: 2px solid var(--border); }
  .sidebar { 
    width: 100%; height: auto; border-right: none; 
    padding: 20px; box-shadow: none; border-radius: 0;
    overflow-y: visible;
  }
}`;

    // There might be some whitespace differences, so let's use a regex to replace everything between @media and the next known clean rule
    const mapColIdx = html.indexOf('.map-col { display: flex;');
    if (mapColIdx !== -1) {
        html = html.substring(0, startIdx) + cleanBlock + '\n\n' + html.substring(mapColIdx);
    }
}

fs.writeFileSync('templates/index.html', html, 'utf8');
