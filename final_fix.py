import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update the heading arrow to be a solid pointer
old_arrow_draw = """ctx.moveTo(Math.max(R_func(32), 24), 0);
  ctx.lineTo(0, -Math.max(R_func(12), 10));
  ctx.lineTo(0, Math.max(R_func(12), 10));
  ctx.closePath();
  
  const grad = ctx.createLinearGradient(0, 0, Math.max(R_func(32), 24), 0);
  grad.addColorStop(0, "rgba(239, 68, 68, 0.9)");
  grad.addColorStop(1, "rgba(239, 68, 68, 0.0)");
  
  ctx.fillStyle = grad;
  ctx.fill();"""

new_arrow_draw = """ctx.moveTo(Math.max(R_func(24), 20), 0); // Tip
  ctx.lineTo(Math.max(R_func(10), 8), -Math.max(R_func(8), 6));
  ctx.lineTo(Math.max(R_func(10), 8), Math.max(R_func(8), 6));
  ctx.closePath();
  
  ctx.fillStyle = "#FFFFFF"; // Solid highly visible white pointer
  ctx.shadowColor = "rgba(0,0,0,0.5)"; ctx.shadowBlur = 4;
  ctx.fill(); ctx.shadowBlur = 0;"""

html = html.replace(old_arrow_draw, new_arrow_draw)

# 2. Fix the Pedometer Speed
html = html.replace('STEP_THRESH: 1.0,', 'STEP_THRESH: 1.5,')
html = html.replace('STEP_LEN: 55,', 'STEP_LEN: 25,')

# 3. Compress the Legend on Mobile
old_sidebar_media = """.sidebar { width: 100%; height: 55vh; border-right: none; border-top: 1px solid var(--border); box-shadow: 0 -4px 16px rgba(0,0,0,0.15); border-top-left-radius: 24px; border-top-right-radius: 24px; padding-top: 24px; padding-bottom: 32px; position: relative; }"""
new_sidebar_media = """.sidebar { width: 100%; height: 55vh; border-right: none; border-top: 1px solid var(--border); box-shadow: 0 -4px 16px rgba(0,0,0,0.15); border-top-left-radius: 24px; border-top-right-radius: 24px; padding-top: 24px; padding-bottom: 60px; position: relative; }
  .legend-sec { display: flex; flex-wrap: wrap; gap: 8px; padding: 12px; }
  .leg-row { width: 45%; margin-bottom: 0; }"""
html = html.replace(old_sidebar_media, new_sidebar_media)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
