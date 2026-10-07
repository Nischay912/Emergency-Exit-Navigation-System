const fs = require('fs');

let html = fs.readFileSync('templates/index.html', 'utf8');

const hazardPatch = `
  // === IICCM HAZARD DETECTION LOGIC ===
  let activeHazards = [];
  
  async function pollHazards() {
    try {
      const res = await fetch('/api/hazards');
      const data = await res.json();
      const newHazards = data.hazards || [];
      
      // If a new hazard appeared, trigger rerouting and voice alert!
      const addedHazards = newHazards.filter(h => !activeHazards.includes(h));
      activeHazards = newHazards;
      
      if (addedHazards.length > 0) {
        // If we are currently navigating and the hazard is on our path, reroute immediately!
        if (typeof NAV !== 'undefined' && NAV.steps && NAV.steps.length > 0 && !NAV.demoRunning) {
          const onPath = NAV.steps.some(step => addedHazards.includes(step.fromPos) || addedHazards.includes(step.toPos) || addedHazards.includes(step.target));
          if (onPath) {
            showToast("ðŸš¨ HAZARD DETECTED AHEAD! Rerouting...", 4000);
            speak(VOICE.lang === 'hi-IN' ? HINDI_PHRASES["ðŸš¨"] || "à¤–à¤¤à¤°à¤¾! à¤®à¤¾à¤°à¥à¤— à¤¬à¤¦à¤² à¤°à¤¹à¤¾ à¤¹à¥ˆ" : "Hazard detected on your path. Recalculating safe route immediately.");
            openNavigation(); // Recalculates based on new hazards
          }
        }
      }
    } catch(e) {}
  }
  
  setInterval(pollHazards, 2000);
`;

const initStart = html.indexOf('async function init(){');
if (initStart !== -1) {
    // insert polling logic before init
    html = html.substring(0, initStart) + hazardPatch + '\n' + html.substring(initStart);
}

// Now modify buildAdj() to ignore edges connecting to activeHazards
const buildAdjStart = html.indexOf('function buildAdj() {');
if (buildAdjStart !== -1) {
    const edgeLoopStart = html.indexOf('GRAPH.edges.forEach(e => {', buildAdjStart);
    if (edgeLoopStart !== -1) {
        const replacement = `GRAPH.edges.forEach(e => {
      // IICCM: Dynamic Rerouting -> Ignore edges connected to active hazards (fires/blockages)
      if (activeHazards.includes(e[0]) || activeHazards.includes(e[1])) return;
      `;
        const oldLoopStart = `GRAPH.edges.forEach(e => {`;
        html = html.replace(oldLoopStart, replacement);
    }
}

// Add a red flame icon to hazardous rooms in render()
const renderRoomStart = html.indexOf('/* === ROOMS === */');
if (renderRoomStart !== -1) {
    const roomLoopBody = html.indexOf('const isUser = name === currentUser;', renderRoomStart);
    if (roomLoopBody !== -1) {
        const replacement = `const isUser = name === currentUser;
    const isHazard = activeHazards.includes(name);
    
    nctx.beginPath();`;
        html = html.replace(`const isUser = name === currentUser;\n    \n    nctx.beginPath();`, replacement);
        html = html.replace(`const isUser = name === currentUser;
    
    ctx.beginPath();`, `const isUser = name === currentUser;
    const isHazard = activeHazards.includes(name);
    ctx.beginPath();`);
        
        // Change fill color if it's a hazard
        html = html.replace('nctx.fillStyle = isUser ? (isDark?"#3b1414":"#FCE8E6") : onPath ? (isDark?"#122a4f":"#E8F0FE") : (isDark?"#242424":"#F1F3F4");', 
        'nctx.fillStyle = isHazard ? "rgba(239, 68, 68, 0.4)" : isUser ? (isDark?"#3b1414":"#FCE8E6") : onPath ? (isDark?"#122a4f":"#E8F0FE") : (isDark?"#242424":"#F1F3F4");');
        
        html = html.replace('ctx.fillStyle = isUser ? (isDark?"#3b1414":"#FCE8E6") : onPath ? (isDark?"#122a4f":"#E8F0FE") : (isDark?"#242424":"#F1F3F4");', 
        'ctx.fillStyle = isHazard ? "rgba(239, 68, 68, 0.4)" : isUser ? (isDark?"#3b1414":"#FCE8E6") : onPath ? (isDark?"#122a4f":"#E8F0FE") : (isDark?"#242424":"#F1F3F4");');
    }
}

fs.writeFileSync('templates/index.html', html, 'utf8');
