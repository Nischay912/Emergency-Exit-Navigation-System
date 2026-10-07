const fs = require('fs');
let html = fs.readFileSync('templates/index.html', 'utf8');

// The crash happens inside renderNavMiniMap
const navRoomsStart = html.indexOf('/* === ROOMS === */', html.indexOf('function renderNavMiniMap'));
if (navRoomsStart !== -1) {
    const navRoomsEnd = html.indexOf('/* === EDGES === */', navRoomsStart);
    if (navRoomsEnd !== -1) {
        let block = html.substring(navRoomsStart, navRoomsEnd);
        // Remove activeHazards
        block = block.replace(/const isHazard = activeHazards\.includes\(name\);\n/g, '');
        block = block.replace(/const isHazard = activeHazards\.includes\(name\);/g, '');
        // Remove the usage of isHazard in fillStyle
        block = block.replace(/isHazard \? "rgba\(239, 68, 68, 0\.4\)" : /g, '');
        
        html = html.substring(0, navRoomsStart) + block + html.substring(navRoomsEnd);
    }
}

fs.writeFileSync('templates/index.html', html, 'utf8');
