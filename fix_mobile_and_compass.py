import os

file_path = 'templates/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix Mobile CSS for Sidebar and Nav Top
old_media = "@media(max-width: 768px) { .sidebar { width: 100%; height: 45vh; border-right: none; border-top: 1px solid var(--border); box-shadow: 0 -2px 10px rgba(0,0,0,0.1); } .app { flex-direction: column-reverse; } }"
new_media = """@media(max-width: 768px) { 
  .sidebar { width: 100%; height: 55vh; border-right: none; border-top: 1px solid var(--border); box-shadow: 0 -4px 16px rgba(0,0,0,0.15); border-top-left-radius: 24px; border-top-right-radius: 24px; padding-top: 24px; padding-bottom: 32px; position: relative; } 
  .sidebar::before { content: ''; position: absolute; top: 8px; left: 50%; transform: translateX(-50%); width: 40px; height: 5px; background: var(--muted); border-radius: 3px; opacity: 0.5; }
  .app { flex-direction: column-reverse; }
  .nav-top { flex-direction: column; align-items: flex-start; padding: 16px; gap: 12px; }
  .nav-arrow-row { display: flex; align-items: center; gap: 12px; width: 100%; }
  .nav-arrow { font-size: 32px; width: 32px; text-align: left; }
  .nav-action { font-size: 20px; }
}"""
if old_media in html:
    html = html.replace(old_media, new_media)
else:
    # Fallback if already modified
    html = html.replace('</style>', new_media + '\n</style>')

# Ensure .nav-arrow-row is flex by default too so it looks good if desktop
css_arrow_row = ".nav-arrow-row { display: flex; align-items: center; gap: 16px; }"
if 'nav-arrow-row {' not in html:
    html = html.replace('</style>', css_arrow_row + '\n</style>')


# 2. Inject Heading Arrow Logic
script_injection = """
function drawHeadingArrow(ctx, x, y, R_func, isDemo) {
  let dx = 0, dy = 0;
  if (isDemo && typeof NAV !== 'undefined' && NAV.demoRunning && NAV.steps && NAV.steps.length > 0) {
    const step = NAV.steps[NAV.currentStep] || NAV.steps[NAV.steps.length - 1];
    if (step && step.toPos && step.fromPos) {
      dx = step.toPos[0] - step.fromPos[0];
      dy = step.toPos[1] - step.fromPos[1];
    }
  } else if (typeof PDR !== 'undefined' && PDR.active) {
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
  // Draw cone pointing right (+X axis)
  ctx.moveTo(Math.max(R_func(32), 24), 0);
  ctx.lineTo(0, -Math.max(R_func(16), 12));
  ctx.lineTo(0, Math.max(R_func(16), 12));
  ctx.closePath();
  
  const grad = ctx.createLinearGradient(0, 0, Math.max(R_func(32), 24), 0);
  grad.addColorStop(0, "rgba(239, 68, 68, 0.9)");
  grad.addColorStop(1, "rgba(239, 68, 68, 0.0)");
  
  ctx.fillStyle = grad;
  ctx.fill();
  ctx.restore();
}
"""
if 'function drawHeadingArrow' not in html:
    html = html.replace('</script>', script_injection + '\n</script>')

# 3. Add to drawWalkOverlay (Main map PDR mode)
old_walk_overlay_draw = """ctx.shadowColor = "#ef4444"; ctx.shadowBlur = R(14);
      ctx.fill(); ctx.shadowBlur = 0;"""
new_walk_overlay_draw = """ctx.shadowColor = "#ef4444"; ctx.shadowBlur = R(14);
      ctx.fill(); ctx.shadowBlur = 0;
      if (typeof drawHeadingArrow === 'function') drawHeadingArrow(ctx, X(PDR.pos.x), Y(PDR.pos.y), R, false);"""
html = html.replace(old_walk_overlay_draw, new_walk_overlay_draw)


# 4. Add to drawDemoPointerOnMiniMap (Nav map Demo mode)
old_demo_pointer = """nctx.beginPath();
  nctx.arc(x, y, Math.max(NR(12), 12), 0, Math.PI*2);
  nctx.fillStyle = "#ef4444";
  nctx.fill();"""
new_demo_pointer = """nctx.beginPath();
  nctx.arc(x, y, Math.max(NR(12), 12), 0, Math.PI*2);
  nctx.fillStyle = "#ef4444";
  nctx.fill();
  if (typeof drawHeadingArrow === 'function') drawHeadingArrow(nctx, x, y, NR, true);"""
html = html.replace(old_demo_pointer, new_demo_pointer)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
