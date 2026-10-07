import re

def update_theme():
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update CSS Variables (Light Theme / Google Maps)
    css_vars = """
:root{
  --bg:#f8f9fa;
  --panel:#ffffff;
  --border:#dadce0;
  --text:#202124;
  --muted:#5f6368;
  --red:#ea4335;
  --green:#34a853;
  --amber:#fbbc04;
  --purple:#1a73e8; /* re-purposed as primary blue */
}
body{margin:0;font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column;}
"""
    content = re.sub(r':root\{[^}]+\}\nbody\{[^}]+\}', css_vars.strip(), content, flags=re.MULTILINE)

    # 2. Update Header & Logo
    content = re.sub(r'background:var\(--panel\);border-bottom:1px solid var\(--border\)', r'background:#ffffff;border-bottom:1px solid #dadce0;box-shadow:0 1px 2px rgba(0,0,0,0.05)', content)
    content = re.sub(r'color:var\(--red\);', r'color:#ea4335;', content)

    # 3. Update Cards
    content = re.sub(r'\.loc-card\{[^}]+\}', r'.loc-card{background:#ffffff;border:1px solid #dadce0;border-radius:12px;padding:12px;box-shadow:0 1px 3px rgba(0,0,0,0.04);}', content)
    content = re.sub(r'\.rec-card\{[^}]+\}', r'.rec-card{background:#e8f0fe;border:1px solid #8ab4f8;border-radius:12px;padding:12px;color:#174ea6;box-shadow:0 1px 3px rgba(0,0,0,0.04);}', content)
    content = re.sub(r'\.rl\{color:#d8b4fe', r'.rl{color:#1a73e8', content)
    content = re.sub(r'\.re\{font-size:1\.3rem;font-weight:900;color:#fff;text-shadow:0 0 10px rgba\(233,213,255,0\.5\)', r'.re{font-size:1.3rem;font-weight:900;color:#174ea6;', content)
    content = re.sub(r'\.rp\{font-size:\.72rem;color:#e9d5ff;', r'.rp{font-size:.72rem;color:#185abc;', content)
    content = re.sub(r'color:#cbd5e1', r'color:#3c4043', content)

    # 4. Update Canvas Rendering in JS
    # Replace background drawing
    bg_old = r'ctx\.fillStyle="#0e1224";ctx\.fillRect\(0,0,canvas\.width,canvas\.height\);'
    bg_new = r'ctx.fillStyle="#f8f9fa";ctx.fillRect(0,0,canvas.width,canvas.height);'
    content = content.replace(bg_old, bg_new)

    # Replace grid drawing
    grid_old = r'''for\(let i=0;i<DW;i\+=40\).*?ctx\.stroke\(\);'''
    grid_new = r'''ctx.strokeStyle="#e8eaed";ctx.lineWidth=R(1);ctx.beginPath();for(let i=0;i<=DW;i+=40){ctx.moveTo(X(i),0);ctx.lineTo(X(i),Y(DH));}for(let i=0;i<=DH;i+=40){ctx.moveTo(0,Y(i));ctx.lineTo(X(DW),Y(i));}ctx.stroke();'''
    content = re.sub(grid_old, grid_new, content, flags=re.DOTALL)

    # Replace Corridors
    corr_old = r'''CORRIDORS\.forEach\(c=>\{\s*drawRoundRect.*?\}\);'''
    corr_new = r'''CORRIDORS.forEach(c=>{ drawRoundRect(X(c.x),Y(c.y),X(c.w),Y(c.h),R(4),"#ffffff","#dadce0",R(1)); });'''
    content = re.sub(corr_old, corr_new, content, flags=re.DOTALL)

    # Replace Edges (Path)
    edge_old = r'''if\(isWalked\) \{\s*ctx\.strokeStyle="rgba\(100, 116, 139, 0\.4\)";ctx\.lineWidth=R\(5\);\s*ctx\.setLineDash\(\[\]\);ctx\.shadowBlur=0;\s*\} else \{\s*ctx\.strokeStyle="#38bdf8";ctx\.lineWidth=R\(7\);\s*ctx\.setLineDash\(\[\]\);ctx\.shadowColor="#0ea5e9";ctx\.shadowBlur=R\(18\);\s*\}'''
    edge_new = r'''if(isWalked) { ctx.strokeStyle="#dadce0";ctx.lineWidth=R(6);ctx.setLineDash([]);ctx.lineCap="round";ctx.lineJoin="round";ctx.shadowBlur=0; } else { ctx.strokeStyle="#1a73e8";ctx.lineWidth=R(6);ctx.setLineDash([]);ctx.lineCap="round";ctx.lineJoin="round";ctx.shadowBlur=0; }'''
    content = re.sub(edge_old, edge_new, content, flags=re.DOTALL)
    
    edge_unp_old = r'ctx\.strokeStyle="rgba\(14, 165, 233, 0\.15\)";ctx\.lineWidth=R\(1\);\s*ctx\.setLineDash\(\[R\(3\),R\(5\)\]\);ctx\.shadowBlur=0;'
    edge_unp_new = r'ctx.strokeStyle="rgba(0,0,0,0)";ctx.lineWidth=R(1);ctx.setLineDash([]);ctx.shadowBlur=0;'
    content = re.sub(edge_unp_old, edge_unp_new, content, flags=re.DOTALL)

    flow_old = r'''ctx\.strokeStyle="rgba\(255,255,255,0\.4\)";ctx\.lineWidth=R\(7\);\s*ctx\.setLineDash\(\[R\(12\),R\(16\)\]\);ctx\.lineDashOffset=-animT\*1\.8;'''
    flow_new = r'''ctx.strokeStyle="rgba(255,255,255,0.8)";ctx.lineWidth=R(2);ctx.setLineDash([R(6),R(12)]);ctx.lineDashOffset=-animT*1.2;'''
    content = re.sub(flow_old, flow_new, content, flags=re.DOTALL)

    # Replace Room Rects (Glassmorphism -> Solid Google Maps)
    room_old = r'''let borderClr, borderW;\s*if\(isUser\).*?ctx\.restore\(\);'''
    room_new = r'''let fillClr, borderClr, borderW;
    if(isUser){ fillClr="#fce8e6"; borderClr="#ea4335"; borderW=R(2.5); }
    else if(onPath){ fillClr="#e8f0fe"; borderClr="#1a73e8"; borderW=R(2.5); }
    else { fillClr="#f1f3f4"; borderClr="#dadce0"; borderW=R(1); }
    ctx.save(); ctx.beginPath();
    if(ctx.roundRect) ctx.roundRect(X(r.x),Y(r.y),X(r.w),Y(r.h),R(6));
    else ctx.rect(X(r.x),Y(r.y),X(r.w),Y(r.h));
    ctx.fillStyle=fillClr; ctx.fill();
    ctx.strokeStyle=borderClr; ctx.lineWidth=borderW; ctx.stroke();
    ctx.restore();'''
    content = re.sub(room_old, room_new, content, flags=re.DOTALL)

    # Room Pill and text
    pill_bg = r'''ctx\.fillStyle=isUser\?"rgba\(239,68,68,0\.25\)":onPath\?"rgba\(245,158,11,0\.2\)":"rgba\(15,22,45,0\.8\)";'''
    pill_bg_new = r'''ctx.fillStyle=isUser?"#ea4335":onPath?"#1a73e8":"rgba(255,255,255,0.7)";'''
    content = re.sub(pill_bg, pill_bg_new, content)
    
    text_color = r'''ctx\.fillStyle=isUser\?"#fca5a5":onPath\?"#fde68a":"#93c5fd";'''
    text_color_new = r'''ctx.fillStyle=isUser?"#ffffff":onPath?"#ffffff":"#3c4043";'''
    content = re.sub(text_color, text_color_new, content)

    # Exit Nodes
    exit_circle = r'''ctx\.fillStyle=isBest\?bestClr:clr;\s*ctx\.shadowColor=isBest\?bestClr:clr;ctx\.shadowBlur=R\(14\);\s*ctx\.fill\(\);ctx\.shadowBlur=0;\s*ctx\.strokeStyle="rgba\(255,255,255,0\.4\)";ctx\.lineWidth=R\(2\);ctx\.stroke\(\);'''
    exit_circle_new = r'''ctx.fillStyle=isBest?"#1a73e8":clr;ctx.fill();ctx.strokeStyle="#ffffff";ctx.lineWidth=R(2);ctx.stroke();'''
    content = re.sub(exit_circle, exit_circle_new, content, flags=re.DOTALL)

    # Crowd Badge & Safest
    badge_bg = r'''ctx\.fillStyle=clr\+"33";'''
    badge_bg_new = r'''ctx.fillStyle="#ffffff";'''
    content = re.sub(badge_bg, badge_bg_new, content)

    exit_lbl = r'''ctx\.fillStyle=isBest\?"rgba\(168,85,247,0\.25\)":"rgba\(10,15,30,0\.8\)";'''
    exit_lbl_new = r'''ctx.fillStyle="#ffffff"; ctx.shadowColor="rgba(0,0,0,0.1)"; ctx.shadowBlur=R(4);'''
    content = re.sub(exit_lbl, exit_lbl_new, content)
    
    exit_txt = r'''ctx\.fillStyle=isBest\?"#e9d5ff":"#cbd5e1";'''
    exit_txt_new = r'''ctx.fillStyle=isBest?"#1a73e8":"#3c4043";'''
    content = re.sub(exit_txt, exit_txt_new, content)

    # Increase CROWD_MULT even more to 50
    content = re.sub(r'const CROWD_MULT=\{Low:1,Medium:.*?,High:.*?\}', 'const CROWD_MULT={Low:1,Medium:5,High:50}', content)
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    update_theme()
    print("Theme updated successfully.")
