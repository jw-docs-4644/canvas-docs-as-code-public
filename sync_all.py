import subprocess
import sys

scripts = [
    "sync_rubrics.py",
    "sync_assignments.py",
    "sync_discussions.py",
    "sync_pages.py",
    "sync_files.py",
    "sync_modules.py",
    "sync_navigation.py",
    "resolve_links.py",
]

for script in scripts:
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"Error running {script}, stopping.")
        sys.exit(result.returncode)

print("Deployment complete, but you will need to go into Canvas to fix the links that couldn't be resolved.")
