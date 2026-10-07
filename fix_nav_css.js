const fs = require('fs');

let html = fs.readFileSync('templates/index.html', 'utf8');

const missingCss = `
.nav-map-wrap { flex: 1; min-height: 200px; position: relative; border-bottom: 1px solid var(--border); }
.nav-map-wrap canvas { width: 100%; height: 100%; display: block; }
`;

if (!html.includes('.nav-map-wrap { flex: 1;')) {
    html = html.replace('</style>', missingCss + '\n</style>');
}

fs.writeFileSync('templates/index.html', html, 'utf8');
