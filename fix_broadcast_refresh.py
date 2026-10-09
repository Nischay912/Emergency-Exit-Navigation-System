import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Change initial state to null
html = html.replace('let lastBroadcastId = 0;', 'let lastBroadcastId = null;')

# 2. Update logic inside pollCrowd
old_logic = '''      // Broadcast logic
      if (st.broadcast && st.broadcast.id > lastBroadcastId) {
        lastBroadcastId = st.broadcast.id;
        
        let bMsg = st.broadcast.message;'''

new_logic = '''      // Broadcast logic
      if (st.broadcast) {
        if (lastBroadcastId === null) {
          lastBroadcastId = st.broadcast.id; // Silent sync on first page load
        } else if (st.broadcast.id > lastBroadcastId) {
          lastBroadcastId = st.broadcast.id;
          
          let bMsg = st.broadcast.message;'''

html = html.replace(old_logic, new_logic)

# Since we opened another block `} else if (...) {`, we need an extra closing brace `}` 
# right after the toast logic.
old_toast_end = '''setTimeout(() => { toast.className = "toast"; }, 10000);
        }
      }'''

new_toast_end = '''setTimeout(() => { toast.className = "toast"; }, 10000);
          }
        }
      }'''

html = html.replace(old_toast_end, new_toast_end)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
