import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add the Download button at the bottom of the Event Log section
event_log_html = """<div class="section-title">EVENT LOG</div>
    <div class="log-box" id="logBox">
      <!-- logs -->
    </div>"""

report_btn_html = """<div class="section-title">EVENT LOG</div>
    <div class="log-box" id="logBox">
      <!-- logs -->
    </div>
    <button onclick="downloadReport()" style="width: 100%; padding: 14px; margin-top: 16px; background: #0f172a; color: white; border: 1px solid #334155; border-radius: 8px; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: 0.2s;">
      &#128196; Download Official Incident Report
    </button>"""

if "Download Official Incident Report" not in html:
    html = html.replace(event_log_html, report_btn_html)

# 2. Add the JavaScript function to generate the report
js_script = """function downloadReport() {
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
    if(haz1 && haz1.innerHTML.includes("Clear")) report += `- Fire at Intersection Mid1: ACTIVE\\n`;
    if(haz2 && haz2.innerHTML.includes("Clear")) report += `- Blockade at East Hallway: ACTIVE\\n`;
    report += `\\n`;

    report += `[SYSTEM EVENT LOG]\\n`;
    const logBox = document.getElementById("logBox");
    if (logBox) {
        // Reverse logs to chronological order for the file
        const logs = Array.from(logBox.children).map(d => d.innerText).reverse();
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
}"""

if "function downloadReport" not in html:
    html = html.replace('function addLog(msg) {', js_script + '\n\n  function addLog(msg) {')

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
