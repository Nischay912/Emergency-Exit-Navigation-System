import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Insert the button after logList
target_html = '<div class="log-list" id="logList"></div>'
button_html = """<div class="log-list" id="logList"></div>
      <button onclick="downloadReport()" class="action-btn" style="margin-top: 16px; background: #2563eb; color: white; border: none; font-weight: bold;">
        &#128196; Download Official Incident Report
      </button>"""

if 'Download Official Incident Report' not in html:
    html = html.replace(target_html, button_html)
else:
    # Remove the old bad injected button if it somehow got in
    html = re.sub(r'<button onclick="downloadReport\(\)".*?>.*?Download Official Incident Report.*?</button>', '', html, flags=re.DOTALL)
    html = html.replace(target_html, button_html)

# 2. Add the JS function (remove old one if it exists first)
js_func = """function downloadReport() {
    const time = new Date().toLocaleString();
    let report = `=================================\\n`;
    report += ` EMERGENCY EVACUATION REPORT\\n`;
    report += ` Generated: ${time}\\n`;
    report += `=================================\\n\\n`;

    const safeCount = document.getElementById("safeCount") ? document.getElementById("safeCount").innerText : "0";
    report += `[PERSONNEL STATUS]\\n`;
    report += `Total Confirmed Safe: ${safeCount} individuals\\n\\n`;

    report += `[HAZARD STATUS]\\n`;
    const haz1 = document.getElementById("haz-fire");
    const haz2 = document.getElementById("haz-deb");
    if(haz1 && !haz1.innerHTML.includes("Clear")) report += `- Fire at Intersection Mid1: ACTIVE\\n`;
    if(haz2 && !haz2.innerHTML.includes("Clear")) report += `- Blockade at East Hallway: ACTIVE\\n`;
    report += `\\n`;

    report += `[SYSTEM EVENT LOG]\\n`;
    const logList = document.getElementById("logList");
    if (logList) {
        // Reverse logs to chronological order for the file
        const logs = Array.from(logList.children).map(d => d.innerText).reverse();
        report += logs.join("\\n") + "\\n";
    }

    report += `\\n=================================\\n`;
    report += `End of Report.\\n`;

    const blob = new Blob([report], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `Evac_Incident_Report_${Date.now()}.txt`;
    a.click();
    
    addLog("&#128196; Incident Report Generated.");
}

function addLog(msg) {"""

# Remove previous injected downloadReport if it exists
html = re.sub(r'function downloadReport\(\) \{.*?\n\}\n\n\s*function addLog\(msg\) \{', 'function addLog(msg) {', html, flags=re.DOTALL)

# Inject correctly
html = html.replace('function addLog(msg) {', js_func)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
