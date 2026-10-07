const fs = require('fs');

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
