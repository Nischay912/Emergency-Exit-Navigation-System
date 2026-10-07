const fs = require('fs');

let html = fs.readFileSync('templates/index.html', 'utf8');

// 1. Add speakStep(NAV.steps.length) to finishDemoWalk()
const finishDemoStart = html.indexOf('function finishDemoWalk() {');
if (finishDemoStart !== -1) {
    const finishDemoEnd = html.indexOf('}', finishDemoStart) + 1;
    let oldFn = html.substring(finishDemoStart, finishDemoEnd);
    let newFn = oldFn.replace('updateNavDisplay();', 'updateNavDisplay();\n  speakStep(NAV.steps.length);');
    html = html.replace(oldFn, newFn);
}

// 2. Fix Live Walk Arrival Logic in PDR.step()
const pdrStepStart = html.indexOf('const near = findNearestNode(PDR.pos.x, PDR.pos.y, 40);');
if (pdrStepStart !== -1) {
    const replacement = `const near = findNearestNode(PDR.pos.x, PDR.pos.y, 40);
  if (near && near !== currentUser) {
    currentUser = near;
    document.getElementById("userLbl").textContent = near.replace(/_/g," ");
    const sel = document.getElementById("locSelect");
    if (sel) sel.value = near;
    showToast("📍 Arrived: " + near.replace(/_/g," "));
    PDR.stepsSinceCorrection = 0;
    PDR.trail = [];

    // Check if we arrived at an EXIT
    if (GRAPH && GRAPH.exit_nodes && GRAPH.exit_nodes.includes(currentUser)) {
      if (document.getElementById("navOverlay") && document.getElementById("navOverlay").classList.contains("active")) {
        openNavigation(); // Recalculates route -> empty steps -> shows "Arrived"
      }
      speak(VOICE.lang === 'hi-IN' ? HINDI_PHRASES["🏁"] : VOICE.lang === 'kn-IN' ? KANNADA_PHRASES["🏁"] : "You have reached the emergency exit. Please evacuate safely.");
      if (PDR.active) toggleWalkMode(); // Auto-stop walking
      return;
    }

    // --- LIVE VOICE NAVIGATION TRIGGER ---
    if (document.getElementById("navOverlay") && document.getElementById("navOverlay").classList.contains("active")) {
      // If nav UI is open, recalculate path from new node
      openNavigation();
      if (NAV.steps && NAV.steps.length > 0) speakStep(0);
    } else {
      // If nav UI is closed, still guide them if Voice is enabled
      announceLiveNavigationStep();
    }
  }`;
  
    // Find the end of the `if (near && near !== currentUser) { ... }` block
    let i = html.indexOf('{', pdrStepStart) + 1;
    let openBraces = 1;
    while (i < html.length && openBraces > 0) {
        if (html[i] === '{') openBraces++;
        else if (html[i] === '}') openBraces--;
        i++;
    }
    
    html = html.substring(0, pdrStepStart) + replacement + html.substring(i);
}

// 3. Fix Mobile Layout to standard vertical scrolling instead of split
const mobileCssStart = html.indexOf('@media(max-width: 768px) {');
if (mobileCssStart !== -1) {
    const mobileCssEnd = html.indexOf('}', html.indexOf('}', mobileCssStart) + 1) + 1; // get to the end of the media query block
    if (mobileCssEnd !== -1) {
      const newMobileCSS = `@media(max-width: 768px) {
  body { height: auto; overflow-y: auto; }
  .app { flex-direction: column; height: auto; overflow: visible; }
  .map-col { min-height: 45vh; max-height: 45vh; flex: none; border-bottom: 2px solid var(--border); }
  .sidebar { 
    width: 100%; height: auto; border-right: none; 
    padding: 20px; box-shadow: none; border-radius: 0;
    overflow-y: visible;
  }
  .sidebar::before { display: none; }
}`;
      html = html.substring(0, mobileCssStart) + newMobileCSS + html.substring(mobileCssEnd);
    }
}


fs.writeFileSync('templates/index.html', html, 'utf8');
