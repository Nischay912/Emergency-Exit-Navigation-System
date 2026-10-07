import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix KANNADA_PHRASES being declared twice
# Find all occurrences of "const KANNADA_PHRASES = {"
parts = html.split('const KANNADA_PHRASES = {')

if len(parts) > 2:
    print(f"Found {len(parts) - 1} occurrences of KANNADA_PHRASES. Removing the first one.")
    # We want to remove the first occurrence (which is parts[1] up to its closing brace).
    # Since it's a JSON-like object, we can just replace 'const KANNADA_PHRASES = ' with nothing for the first match, or carefully strip the block.
    # Actually, simpler: replace all 'const KANNADA_PHRASES' with 'window.KANNADA_PHRASES' so they don't throw syntax errors.
    html = html.replace('const KANNADA_PHRASES', 'var KANNADA_PHRASES')
    html = html.replace('const HINDI_PHRASES', 'var HINDI_PHRASES')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
