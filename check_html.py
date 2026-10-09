import os
import sys

def check_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    script_start = content.find('<script>')
    script_end = content.find('</script>', script_start)
    
    if script_start != -1 and script_end != -1:
        js_code = content[script_start+8:script_end]
        try:
            # We can't strictly compile JS in Python, but we can check if we broke string literals
            pass
        except Exception as e:
            pass

    print("Checking for mismatched divs...")
    div_opens = content.count('<div')
    div_closes = content.count('</div')
    print(f"<div count: {div_opens}, </div count: {div_closes}")

check_html('templates/index.html')
