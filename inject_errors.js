const fs = require('fs');
let html = fs.readFileSync('templates/index.html', 'utf8');

const injection = `
window.addEventListener('error', function(event) {
    fetch('/log_error?msg=' + encodeURIComponent('Error: ' + event.message + ' at ' + event.filename + ':' + event.lineno));
});
window.addEventListener('unhandledrejection', function(event) {
    fetch('/log_error?msg=' + encodeURIComponent('PromiseRejection: ' + (event.reason && event.reason.stack ? event.reason.stack : event.reason)));
});
`;

html = html.replace('<script>', '<script>' + injection);
fs.writeFileSync('templates/index.html', html, 'utf8');
