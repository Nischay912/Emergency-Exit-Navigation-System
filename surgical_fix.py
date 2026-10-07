import os

file_path = 'templates/index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix corrupted emojis
emoji_map = {
    'dY??': '✅',
    'dY"?': '📍',
    'dY-,?': '🗺️',
    'dYs': '🚪',
    'dY"\'': '🔴',
    'dY"': '📱'
}
for bad, good in emoji_map.items():
    html = html.replace(bad, good)
    
# 2. Fix the Dijkstra crash
old_dijkstra = """    /* === DIJKSTRA === */
    const adj = buildAdj();
    const {dist, prev} = dijkstra(currentUser, adj);
    let bExit = null, bCost = Infinity;
    GRAPH.exit_nodes.forEach(e => { if(dist[e]<bCost){bCost=dist[e];bExit=e;} });
    bestExit = bExit;
    const path = bExit ? getPath(prev, currentUser, bExit) : [];"""

safe_dijkstra = """    /* === DIJKSTRA === */
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
    }"""
html = html.replace(old_dijkstra, safe_dijkstra)

# 3. Add speakStep to finishDemoWalk so Voice says "You have arrived"
old_finish = """function finishDemoWalk() {
  document.getElementById("navAction").textContent = "\uD83C\uDFC1 You have arrived!";
  document.getElementById("navArrow").textContent = "\uD83C\uDFC1";
  document.getElementById("navTarget").textContent = "";
  document.getElementById("navDist").textContent = "";
  document.getElementById("navNextCard").style.display = "none";
  document.getElementById("navProgFill").style.width = "100%";
  document.getElementById("navProgLabel").textContent = "Arrived!";
  document.getElementById("navProgDist").textContent = "0m remaining";
  updateNavDisplay();
}"""

new_finish = """function finishDemoWalk() {
  document.getElementById("navAction").textContent = "\uD83C\uDFC1 You have arrived!";
  document.getElementById("navArrow").textContent = "\uD83C\uDFC1";
  document.getElementById("navTarget").textContent = "";
  document.getElementById("navDist").textContent = "";
  document.getElementById("navNextCard").style.display = "none";
  document.getElementById("navProgFill").style.width = "100%";
  document.getElementById("navProgLabel").textContent = "Arrived!";
  document.getElementById("navProgDist").textContent = "0m remaining";
  updateNavDisplay();
  speakStep(NAV.steps.length);
}"""
html = html.replace(old_finish, new_finish)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
