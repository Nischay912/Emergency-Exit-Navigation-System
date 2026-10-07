const fs = require('fs');

// 1. Fix the blank map bug in index.html
let html = fs.readFileSync('templates/index.html', 'utf8');

const dijkstraCall = `    /* === DIJKSTRA === */
    const adj = buildAdj();
    const {dist, prev} = dijkstra(currentUser, adj);`;

const safeDijkstraCall = `    /* === DIJKSTRA === */
    const adj = buildAdj();
    let dist = {}, prev = {}, path = [];
    if (currentUser && GRAPH.nodes[currentUser]) {
      const res = dijkstra(currentUser, adj);
      dist = res.dist; prev = res.prev;
      let bExit = null, bCost = Infinity;
      GRAPH.exit_nodes.forEach(e => { if(dist[e]<bCost){bCost=dist[e];bExit=e;} });
      bestExit = bExit;
      path = bExit ? getPath(prev, currentUser, bExit) : [];
    } else {
      bestExit = null;
    }`;

// Replace the block of code that crashes
const oldBlockStart = html.indexOf('/* === DIJKSTRA === */');
if (oldBlockStart !== -1) {
    const oldBlockEnd = html.indexOf('/* === CORRIDORS === */', oldBlockStart);
    if (oldBlockEnd !== -1) {
        html = html.substring(0, oldBlockStart) + safeDijkstraCall + '\n\n    ' + html.substring(oldBlockEnd);
    }
}
fs.writeFileSync('templates/index.html', html, 'utf8');


// 2. Fix the hardcoded map file in app.py
let py = fs.readFileSync('app.py', 'utf8');
py = py.replace('GRAPH_FILE = DATA / "floor_graph.json"', 'GRAPH_FILE = DATA / "map_layout.json"');
fs.writeFileSync('app.py', py, 'utf8');
