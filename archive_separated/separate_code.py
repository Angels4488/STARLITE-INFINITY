
import os
import re

source_dir = '/home/starlite/STARLITE-INFINITY/archive_separated'
confessions_dir = os.path.join(source_dir, 'confessions')
mainmodules_file = os.path.join(source_dir, 'MAINMODULES.txt')

files_to_process = [
    'ARK-CONVO.TXT',
    'ARK-CONVO1.5.TXT',
    'ARKS.TXT',
    'ARKS3.TXT',
    'MASTER_CONVO.TXT',
    'THE_CURE.TXT'
]

# Simple python detection: starts with import, from, class, def, or is within ```python block
# Or lines that follow 'Python' header.

def extract_content(content):
    python_blocks = []
    commentary_blocks = []
    
    # 1. Look for markdown code blocks first
    code_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL | re.IGNORECASE)
    # Remove them from content to avoid double processing
    content_remaining = re.sub(r'```python\n(.*?)\n```', 'CODE_BLOCK_PLACEHOLDER', content, flags=re.DOTALL | re.IGNORECASE)
    python_blocks.extend(code_blocks)
    
    # 2. Look for "Python" followed by code
    # Often formatted as:
    # Python
    # class ...
    # ...
    # next section
    python_header_blocks = re.findall(r'\nPython\n(.*?)(?=\n\n|\n[A-Z][a-z]+|\Z)', content_remaining, re.DOTALL)
    for block in python_header_blocks:
        if 'class ' in block or 'def ' in block or 'import ' in block:
            python_blocks.append(block.strip())
            content_remaining = content_remaining.replace(block, 'CODE_BLOCK_PLACEHOLDER')

    # 3. Look for remaining blocks that look like python
    # This is trickier. We can split by paragraphs and check if they look like code.
    paragraphs = content_remaining.split('\n\n')
    final_commentary = []
    for p in paragraphs:
        if 'CODE_BLOCK_PLACEHOLDER' in p:
            # Already extracted parts
            cleaned_p = p.replace('CODE_BLOCK_PLACEHOLDER', '').strip()
            if cleaned_p:
                final_commentary.append(cleaned_p)
            continue
        
        # Heuristic for python code: starts with common keywords and has pythonic structure
        lines = p.strip().split('\n')
        if not lines:
            continue
            
        is_python = False
        first_line = lines[0].strip()
        if first_line.startswith(('import ', 'from ', 'class ', 'def ', '#!/usr/bin/python')):
            is_python = True
        elif len(lines) > 2 and any(l.strip().startswith(('class ', 'def ')) for l in lines[:3]):
            is_python = True
            
        if is_python:
            python_blocks.append(p.strip())
        else:
            final_commentary.append(p.strip())
            
    return python_blocks, "\n\n".join(final_commentary)

# Clear MAINMODULES.txt
with open(mainmodules_file, 'w') as f:
    f.write('')

for filename in files_to_process:
    path = os.path.join(source_dir, filename)
    if not os.path.exists(path):
        print(f"Skipping {filename}, not found.")
        continue
        
    print(f"Processing {filename}...")
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    py_blocks, commentary = extract_content(content)
    
    # Write python blocks to MAINMODULES.txt
    with open(mainmodules_file, 'a', encoding='utf-8') as f:
        for block in py_blocks:
            f.write(f"# --- Extracted from {filename} ---\n")
            f.write(block.strip())
            f.write("\n\n")
            
    # Write commentary to confessions folder
    conf_path = os.path.join(confessions_dir, filename)
    with open(conf_path, 'w', encoding='utf-8') as f:
        f.write(commentary)

print("Separation complete.")
