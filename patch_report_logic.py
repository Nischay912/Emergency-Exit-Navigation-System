import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the hazard logic and move the addLog above the report generation
old_logic = """    const haz1 = document.getElementById("haz-fire");
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
    
    if(typeof addLog === 'function') addLog("&#128196; Incident Report Generated.");"""

new_logic = """    if(typeof addLog === 'function') addLog("&#128196; Incident Report Generated.");

    const haz1 = document.getElementById("haz-fire");
    const haz2 = document.getElementById("haz-deb");
    
    // Check if the button text is white (which means it's active in the UI)
    let fireActive = haz1 && (haz1.style.color === 'white' || haz1.style.color === 'rgb(255, 255, 255)');
    let debActive = haz2 && (haz2.style.color === 'white' || haz2.style.color === 'rgb(255, 255, 255)');
    
    if(fireActive) report += `- Fire at Staff Lounge: ACTIVE\\n`;
    if(debActive) report += `- Blockade at East Hallway: ACTIVE\\n`;
    if(!fireActive && !debActive) report += `- No active hazards.\\n`;
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
    a.click();"""

html = html.replace(old_logic, new_logic)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
