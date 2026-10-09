import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update addLog to save to sessionStorage
old_addlog = """function addLog(msg) {
    const logList = document.getElementById("logList");
    const t = new Date().toLocaleTimeString();
    logList.innerHTML = `<div class="log-item">[${t}] ${msg}</div>` + logList.innerHTML;
  }"""
new_addlog = """function addLog(msg) {
    const logList = document.getElementById("logList");
    const t = new Date().toLocaleTimeString();
    logList.innerHTML = `<div class="log-item">[${t}] ${msg}</div>` + logList.innerHTML;
    sessionStorage.setItem('admin_events', logList.innerHTML);
  }"""
if "sessionStorage.setItem('admin_events'" not in html:
    html = html.replace(old_addlog, new_addlog)

# 2. Update init code in admin.html
# Find the setInterval(refreshAll,4000); in start().
old_start = """setInterval(refreshAll,4000);
  }"""

new_start = """setInterval(refreshAll,4000);
    
    // RESTORE STATE
    const savedLogs = sessionStorage.getItem('admin_events');
    if(savedLogs) document.getElementById('logList').innerHTML = savedLogs;
    
    if(sessionStorage.getItem('admin_sim') === 'true') toggleSim();
    
    // SOURCE OF TRUTH SYNC
    fetch('/api/status').then(r=>r.json()).then(data => {
        if(data.hazards) {
            if(data.hazards.includes('Intersection_Mid1')) {
                const b = document.getElementById('haz-fire');
                if(b) { b.style.background = 'var(--red)'; b.style.color = 'white'; }
            }
            if(data.hazards.includes('Corridor_East')) {
                const b = document.getElementById('haz-deb');
                if(b) { b.style.background = 'var(--amber)'; b.style.color = 'white'; }
            }
        }
        if(data.smoke_level && data.smoke_level !== 'none') {
            currentSmoke = data.smoke_level;
            updateSmokeUI();
        }
    });
  }"""
if "SOURCE OF TRUTH SYNC" not in html:
    html = html.replace(old_start, new_start)

# 3. Update Sim button to save state
old_sim = """if(simRunning){b.innerHTML="&#9209; Stop Simulation";b.className="action-btn btn-stop";simStep();simInterval=setInterval(simStep,4000);}
    else{b.innerHTML="&#127922; Start Auto-Simulate";b.className="action-btn btn-purple";clearInterval(simInterval);}"""
new_sim = """if(simRunning){
      b.innerHTML="&#9209; Stop Simulation";b.className="action-btn btn-stop";
      simStep();simInterval=setInterval(simStep,4000);
      sessionStorage.setItem('admin_sim', 'true');
    } else {
      b.innerHTML="&#127922; Start Auto-Simulate";b.className="action-btn btn-purple";
      clearInterval(simInterval);
      sessionStorage.setItem('admin_sim', 'false');
    }"""
if "sessionStorage.setItem('admin_sim'" not in html:
    html = html.replace(old_sim, new_sim)


with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
