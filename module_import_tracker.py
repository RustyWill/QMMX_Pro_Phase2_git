import os
import ast

project_root = os.path.dirname(__file__)
all_py_files = []
imported_modules = set()

# Step 1: Collect all Python files
for root, dirs, files in os.walk(project_root):
    for file in files:
        if file.endswith('.py'):
            full_path = os.path.join(root, file)
            all_py_files.append(full_path)

# Step 2: Parse each file to detect imports
for file_path in all_py_files:
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            node = ast.parse(f.read(), filename=file_path)
            for n in ast.walk(node):
                if isinstance(n, ast.Import):
                    for alias in n.names:
                        imported_modules.add(alias.name.split('.')[0])
                elif isinstance(n, ast.ImportFrom):
                    if n.module:
                        imported_modules.add(n.module.split('.')[0])
        except Exception as e:
            print(f"⚠️ Error parsing {file_path}: {e}")

# Step 3: Compare against known files
print("\n📦 QMMX Import Tracker\n--------------------------")
for file_path in sorted(all_py_files):
    name = os.path.splitext(os.path.basename(file_path))[0]
    rel_path = os.path.relpath(file_path, project_root)

    if name in imported_modules:
        print(f"✅ USED:    {rel_path}")
    else:
        print(f"❌ UNUSED?: {rel_path}")
