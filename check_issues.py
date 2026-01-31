import re

files = ['INTEGRATION_GUIDE.md', 'STARLITE_AS_COMPANION.md']
issue_count = 0

for filename in files:
    with open(filename, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    print(f"\n=== {filename} ===")
    
    # Check 1: Trailing whitespace
    trailing = sum(1 for line in lines if line.endswith(' ') or line.endswith('\t'))
    print(f"Trailing whitespace: {trailing}")
    issue_count += trailing
    
    # Check 2: Line length > 120
    long_lines = sum(1 for line in lines if len(line) > 120)
    print(f"Lines > 120 chars: {long_lines}")
    issue_count += long_lines
    
    # Check 3: Broken file references
    broken_refs = re.findall(r'\[([^\]]+)\]\(([^)]+\.py)\)', content)
    print(f"Potential file reference issues: {len(broken_refs)}")
    
    # Check 4: Missing code fence closes
    fence_count = content.count('```')
    if fence_count % 2 != 0:
        print(f"⚠️ Unclosed code fence (count: {fence_count})")
        issue_count += 1

print(f"\nTotal issues found: {issue_count}")
print(f"(Note: This analysis is approximate)")
