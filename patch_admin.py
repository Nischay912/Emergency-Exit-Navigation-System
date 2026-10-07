import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

admin_upload_ui = """
  <div class="card" style="margin-top:20px; border-color: #3b82f6;">
    <div class="card-header" style="background:#3b82f6;">Upload Map JSON</div>
    <div style="padding:15px;">
      <p style="font-size:0.8rem; color:#666; margin-bottom:10px;">Upload a custom layout map (JSON format) containing rooms, corridors, and node positions to dynamically update the UI.</p>
      <input type="file" id="mapUpload" accept=".json" style="margin-bottom:10px;">
      <button class="action-btn btn-blue" onclick="uploadMap()">Upload New Map Layout</button>
    </div>
  </div>
</div>
"""

upload_script = """
async function uploadMap() {
  const fileInput = document.getElementById("mapUpload");
  if (!fileInput.files.length) return alert("Please select a JSON file first.");
  const file = fileInput.files[0];
  const reader = new FileReader();
  reader.onload = async function(e) {
    try {
      const data = JSON.parse(e.target.result);
      const r = await fetch("/api/layout", {
        method: "POST",
        body: JSON.stringify(data)
      });
      if (r.ok) alert("Map Layout Updated Successfully! The user UI will now render this new layout.");
      else alert("Failed to update layout.");
    } catch(err) {
      alert("Invalid JSON file.");
    }
  };
  reader.readAsText(file);
}

// Add blue button CSS if not exists
"""

if 'Upload New Map Layout' not in content:
    content = content.replace('</div>\n\n<script>', admin_upload_ui + '\n<script>')
    content = content.replace('</script>\n</body>', upload_script + '\n</script>\n</body>')
    # Add btn-blue css
    content = content.replace('.btn-stop{background:#ef4444;color:#fff;}', '.btn-stop{background:#ef4444;color:#fff;}\n.btn-blue{background:#3b82f6;color:#fff;}')

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)
