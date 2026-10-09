import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

js_func = """
function downloadReport() {
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
    
    if(typeof addLog === 'function') addLog("&#128196; Incident Report Generated.");
}
"""

# Just inject it right before the closing script tag.
if 'function downloadReport' not in html:
    html = html.replace('</script>\n</body>', js_func + '\n</script>\n</body>')

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
