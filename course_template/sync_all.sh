#!/bin/bash

# Resolve the directory containing this script (the course folder),
# regardless of what it's named or where it's called from.
COURSE_DIR="$(cd "$(dirname "$BASH_SOURCE")" && pwd)"
SCRIPTS_DIR="$(dirname "$COURSE_DIR")"

cd "$COURSE_DIR"

python3 "$SCRIPTS_DIR/sync_rubrics.py"
python3 "$SCRIPTS_DIR/sync_assignments.py"
python3 "$SCRIPTS_DIR/sync_discussions.py"
python3 "$SCRIPTS_DIR/sync_pages.py"
python3 "$SCRIPTS_DIR/sync_files.py"
python3 "$SCRIPTS_DIR/sync_modules.py"
python3 "$SCRIPTS_DIR/sync_navigation.py"
python3 "$SCRIPTS_DIR/resolve_links.py"

echo "Deployment complete, but you will need to go into Canvas to fix the links that couldn't be resolved."
