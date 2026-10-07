import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Re-inject drawHeadingArrow (It was accidentally deleted because of a typo in the replace string)
arrow_logic = """
function drawHeadingArrow(ctx, x, y, R_func, isDemo) {
  let dx = 0, dy = 0;
  if (isDemo && typeof NAV !== 'undefined' && NAV.demoRunning && NAV.steps && NAV.steps.length > 0) {
    const step = NAV.steps[NAV.currentStep] || NAV.steps[NAV.steps.length - 1];
    if (step && step.toPos && step.fromPos) {
      dx = step.toPos[0] - step.fromPos[0];
      dy = step.toPos[1] - step.fromPos[1];
    }
  } else if (typeof PDR !== 'undefined' && PDR.sensorsEnabled) {
    // Show arrow anytime sensors are enabled (so they can calibrate)
    const mapHeading = ((PDR.heading - PDR.northOffset) + 360) % 360;
    const rad = mapHeading * Math.PI / 180;
    dx = Math.sin(rad);
    dy = -Math.cos(rad);
  }
  
  if (dx === 0 && dy === 0) return;
  const angle = Math.atan2(dy, dx);
  
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  ctx.beginPath();
  ctx.moveTo(Math.max(R_func(24), 20), 0); // Tip
  ctx.lineTo(Math.max(R_func(10), 8), -Math.max(R_func(8), 6));
  ctx.lineTo(Math.max(R_func(10), 8), Math.max(R_func(8), 6));
  ctx.closePath();
  
  ctx.fillStyle = "#FFFFFF"; // Solid highly visible white pointer
  ctx.shadowColor = "rgba(0,0,0,0.5)"; ctx.shadowBlur = 4;
  ctx.fill(); ctx.shadowBlur = 0;
  ctx.restore();
}
"""

if 'function drawHeadingArrow' not in html:
    html = html.replace('async function init(){', arrow_logic + '\nasync function init(){')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
