import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timezone
from dateutil import parser
from canvasapi import Canvas
from config_loader import load_canvas_config, load_course_id

API_URL, API_KEY = load_canvas_config()
API_URL = API_URL.rstrip('/')
COURSE_ID = load_course_id()

class FileSyncer:
    # Files/patterns that should NEVER be uploaded to Canvas
    BLOCKED_PATTERNS = {
        '.env',           # Environment variables
        '.git',           # Git directory
        '__pycache__',    # Python cache
        '.sync_cache_',   # Sync cache files
        '.venv',          # Virtual environment
        'venv',
        '.DS_Store',      # macOS
        'Thumbs.db',      # Windows
        '.gitignore',
        '.gitkeep',
    }

    def __init__(self):
        self.canvas = Canvas(API_URL, API_KEY)
        self.course = self.canvas.get_course(COURSE_ID)
        # Dictionary to store { "path/filename": "updated_at_datetime" }
        self.remote_files = self._map_remote_files()

    def _should_skip_file(self, filename, filepath):
        """Check if a file matches blocked patterns and should not be uploaded."""
        # Check filename directly
        if filename in self.BLOCKED_PATTERNS:
            return True

        # Check for blocked patterns in path
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in filepath:
                return True

        return False

    def _map_remote_files(self):
        """Builds a map of existing files and their last update time."""
        print("Indexing Canvas files... (this may take a moment)")
        file_map = {}
        folders = {f.id: f.full_name for f in self.course.get_folders()}
        
        for f in self.course.get_files():
            # Standardize path to match local (e.g., "course files/Images/logo.png")
            folder_path = folders.get(f.folder_id, "course files")
            # Remove the root 'course files' to match local 'Files' folder structure
            clean_path = folder_path.replace("course files", "").strip("/")
            full_key = os.path.join(clean_path, f.display_name).strip("/")
            
            # Convert Canvas ISO timestamp to a Python datetime object
            file_map[full_key] = parser.parse(f.updated_at)
        return file_map

    def sync(self, local_root="Files"):
        print(f"--- Starting Delta Sync from {local_root} ---")

        for root, dirs, files in os.walk(local_root):
            for filename in files:
                local_path = os.path.join(root, filename)
                relative_path = os.path.relpath(local_path, local_root)

                # Safety check: skip blocked files
                if self._should_skip_file(filename, relative_path):
                    print(f"[BLOCKED] {relative_path} (security safeguard)")
                    continue
                
                # Get local modified time (converted to UTC for comparison)
                mtime = os.path.getmtime(local_path)
                local_mod_time = datetime.fromtimestamp(mtime, tz=timezone.utc)

                # Check if we need to upload
                should_upload = False
                if relative_path not in self.remote_files:
                    print(f"[NEW] {relative_path}")
                    should_upload = True
                else:
                    remote_mod_time = self.remote_files[relative_path]
                    if local_mod_time > remote_mod_time:
                        print(f"[UPDATED] {relative_path}")
                        should_upload = True
                    else:
                        # Skip if local is older or same age
                        continue

                if should_upload:
                    canvas_folder = "course files"
                    sub_dir = os.path.relpath(root, local_root)
                    if sub_dir != ".":
                        canvas_folder += f"/{sub_dir}"

                    self.course.upload(
                        local_path,
                        parent_folder_path=canvas_folder,
                        on_duplicate="overwrite"
                    )

if __name__ == "__main__":
    syncer = FileSyncer()
    syncer.sync()
