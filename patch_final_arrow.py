import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Clean up multiple injections of drawHeadingArrow
# Remove all existing drawHeadingArrow functions
html = re.sub(r'function drawHeadingArrow\([^)]+\)\s*\{.*?\n\}\n', '', html, flags=re.DOTALL)

# Inject it exactly ONCE before init()
arrow_logic = """
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
  ctx.moveTo(Math.max(R_func(32), 24), 0);
  ctx.lineTo(0, -Math.max(R_func(12), 10));
  ctx.lineTo(0, Math.max(R_func(12), 10));
  ctx.closePath();
  
  const grad = ctx.createLinearGradient(0, 0, Math.max(R_func(32), 24), 0);
  grad.addColorStop(0, "rgba(239, 68, 68, 0.9)");
  grad.addColorStop(1, "rgba(239, 68, 68, 0.0)");
  
  ctx.fillStyle = grad;
  ctx.fill();
  ctx.restore();
}
"""
html = html.replace('function init() {', arrow_logic + '\nfunction init() {')

# 2. Inject call into drawWalkOverlay (Free-moving dot)
html = re.sub(
    r'(ctx\.fill\(\);\s*ctx\.shadowBlur\s*=\s*0;)',
    r'\1\n      if (typeof drawHeadingArrow === "function") drawHeadingArrow(ctx, X(PDR.pos.x), Y(PDR.pos.y), R, false);',
    html
)

# 3. Inject call into render (Main Map User Pin)
html = re.sub(
    r'(ctx\.arc\(ux,\s*uy,\s*R\(14\)\s*\*\s*pulse,\s*0,\s*Math\.PI\s*\*\s*2\);\s*ctx\.fillStyle\s*=[^;]+;\s*ctx\.fill\(\);)',
    r'\1\n      if (typeof drawHeadingArrow === "function") drawHeadingArrow(ctx, ux, uy, R, false);',
    html
)


# 4. Fix Pedometer / Walking Speed (Increase Step Length and Sensitivity)
html = html.replace('STEP_THRESH: 1.8,', 'STEP_THRESH: 1.0,')
html = html.replace('STEP_LEN: 22,', 'STEP_LEN: 55,')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
