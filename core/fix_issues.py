import os
import ast
import py_compile
import sys
import re
import argparse

def get_all_python_files(root_dir):
    """Get all Python files in the workspace recursively, excluding common dirs."""
    exclude_dirs = {
        '.venv', 'venv', '__pycache__', '.git', 'node_modules', '.vscode',
        'snap', '.config', '.vscode-insiders', 'data', 'logs', 'runtime',
        'archive_research', 'AetherJarvis_safe'
    }
    python_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Modify dirnames in place to skip excluded dirs
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for filename in filenames:
            if filename.endswith('.py'):
                python_files.append(os.path.join(dirpath, filename))
    return python_files

def check_syntax(file_path):
    """Check syntax of a Python file using ast.parse."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source, filename=file_path)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error parsing: {str(e)}"

def check_imports(file_path):
    """Check for import issues by attempting to compile."""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Compilation error: {str(e)}"

def fix_trailing_whitespace(file_path):
    """Remove trailing whitespace from all lines in the file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        original_lines = lines[:]
        lines = [line.rstrip() + '\n' for line in lines]

        # Remove trailing newline if the file didn't end with one
        if original_lines and not original_lines[-1].endswith('\n'):
            lines[-1] = lines[-1].rstrip('\n')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return True
    except Exception as e:
        return False, str(e)

def check_line_lengths(file_path, max_length=120):
    """Check for lines exceeding max_length."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        long_lines = []
        for i, line in enumerate(lines, 1):
            if len(line.rstrip()) > max_length:
                long_lines.append((i, len(line.rstrip())))

        return long_lines, None
    except Exception as e:
        return [], str(e)

def main():
    parser = argparse.ArgumentParser(description="STARLITE-INFINITY Workspace Issue Fixer")
    parser.add_argument('--fix', action='store_true', help="Automatically fix issues like trailing whitespace.")
    parser.add_argument('--max-line', type=int, default=120, help="Maximum allowed line length.")
    parser.add_argument('--verbose', action='store_true', help="Show detailed output for each file.")
    args = parser.parse_args()

    # Get the workspace root (assuming script is in STARLITE-INFINITY, go up one level)
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"🔍 Scanning workspace: {workspace_root}")

    python_files = get_all_python_files(workspace_root)
    print(f"📁 Found {len(python_files)} Python files")

    issues_found = 0
    files_fixed = 0

    for file_path in python_files:
        relative_path = os.path.relpath(file_path, workspace_root)
        if args.verbose:
            print(f"\n🔧 Processing: {relative_path}")

        # Check syntax
        syntax_ok, syntax_error = check_syntax(file_path)
        if not syntax_ok:
            print(f"❌ {relative_path}: Syntax error: {syntax_error}")
            issues_found += 1
            continue
        else:
            if args.verbose: print("  ✅ Syntax OK")

        # Check imports/compilation
        import_ok, import_error = check_imports(file_path)
        if not import_ok:
            if args.verbose: print(f"  ❌ Compilation issue: {import_error}")
        else:
            if args.verbose: print("  ✅ Compilation OK")

        # Check line lengths
        long_lines, length_error = check_line_lengths(file_path, args.max_line)
        if long_lines:
            if args.verbose: print(f"  ⚠️ {len(long_lines)} lines exceed {args.max_line} characters")
            issues_found += len(long_lines)

        # Fix issues if requested
        if args.fix:
            fixed, fix_error = fix_trailing_whitespace(file_path)
            if fixed:
                if args.verbose: print("  ✨ Fixed trailing whitespace")
                files_fixed += 1

    print("\n" + "="*40)
    print("📊 STARLITE-INFINITY Workspace Summary")
    print(f"Files processed: {len(python_files)}")
    print(f"Issues identified: {issues_found}")
    if args.fix:
        print(f"Files auto-fixed: {files_fixed}")
    print("="*40)

if __name__ == "__main__":
    main()
        if not import_ok:
            print(f"❌ Import/Compilation error: {import_error}")
            issues_found += 1
        else:
            print("✅ Imports OK")

        # Fix trailing whitespace
        whitespace_fixed = fix_trailing_whitespace(file_path)
        if whitespace_fixed:
            print("✅ Trailing whitespace removed")
            files_fixed += 1
        else:
            print("⚠️  Could not fix trailing whitespace")

        # Check line lengths
        long_lines = check_line_lengths(file_path)
        if long_lines:
            print(f"⚠️  {len(long_lines)} lines exceed 120 characters")
            for line_num, length in long_lines[:5]:  # Show first 5
                print(f"   Line {line_num}: {length} chars")
            if len(long_lines) > 5:
                print(f"   ... and {len(long_lines) - 5} more")
        else:
            print("✅ Line lengths OK")

    print("\n📊 Summary:")
    print(f"   Files scanned: {len(python_files)}")
    print(f"   Issues found: {issues_found}")
    print(f"   Files fixed: {files_fixed}")

    if issues_found == 0:
        print("🎉 No issues found!")
    else:
        print("⚠️  Some issues require manual attention.")

if __name__ == "__main__":
    main()
