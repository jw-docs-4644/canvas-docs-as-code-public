import os
import subprocess
import frontmatter
import re
import json
import hashlib
from canvasapi import Canvas
from config_loader import load_canvas_config, load_course_id

# 1. SETUP
API_URL, API_KEY = load_canvas_config()
COURSE_ID = load_course_id()

SOURCE_DIR = "Assignments"  # Points to Assignments folder
DEFAULT_POINTS = 20
PUBLISH = True
CACHE_FILE = ".sync_cache_assignments.json"

def get_file_hash(data_dict):
    """Creates a unique MD5 hash of the assignment data."""
    encoded = json.dumps(data_dict, sort_keys=True).encode()
    return hashlib.md5(encoded).hexdigest()

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except: return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def extract_h1(markdown_text):
    """Finds the first H1 in the markdown string."""
    match = re.search(r'^#\s+(.+)$', markdown_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def sync_assignments():
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Folder '{SOURCE_DIR}' not found.")
        return

    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(COURSE_ID)
    cache = load_cache()
    
    print(f"Syncing Assignments for: {course.name}")
    
    # Pre-fetch rubrics and existing assignments
    print("Fetching metadata from Canvas...")
    canvas_rubrics = {r.title: r.id for r in course.get_rubrics()}
    existing_assignments = {a.name: a for a in course.get_assignments()}

    for md_filename in os.listdir(SOURCE_DIR):
        if not md_filename.endswith('.md'):
            continue
        
        md_path = os.path.join(SOURCE_DIR, md_filename)
        
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
        except Exception as e:
            print(f"[!] YAML ERROR in '{md_filename}': {e}")
            continue

        # --- 1. PREPARE DATA FOR HASHING ---
        nice_title = extract_h1(post.content)
        if not nice_title:
            nice_title = md_filename.replace(".md", "").replace("_", " ").title()

        file_points = post.get('points', DEFAULT_POINTS)
        target_rubric = post.get('rubric', "None")

        sub_types = post.get('submission_types', ['online_upload'])
        
        # Include all relevant metadata in the hash
        check_data = {
            'title': nice_title,
            'points': file_points,
            'rubric': target_rubric,
            'content': post.content,
            'peer_reviews': post.get('peer_reviews', False),
            'file_types': post.get('file_types', []),
            'submission_types': post.get('submission_types', ['online_upload'])
        }
        current_hash = get_file_hash(check_data)

        # --- 2. THE SMART GATEKEEPER ---
        if cache.get(md_filename) == current_hash and nice_title in existing_assignments:
            print(f"⏩ Skipping: '{nice_title}' (No changes detected)")
            continue

        # --- 3. IF WE ARE HERE, SOMETHING CHANGED -> PROCESS ---
        print(f"🚀 Processing: '{nice_title}'")
        
        # Remove H1 from body for Pandoc
        body_content = re.sub(r'^#\s+.+$', '', post.content, count=1, flags=re.MULTILINE).strip()

        try:
            process = subprocess.run(
                ['pandoc', '-f', 'markdown', '-t', 'html'],
                input=body_content, text=True, capture_output=True, check=True
            )
            html_body = process.stdout
        except subprocess.CalledProcessError as e:
            print(f"Pandoc error on {md_filename}: {e}")
            continue

        assignment_data = {
            'name': nice_title,
            'description': html_body,
            'points_possible': file_points,
            'grading_type': post.get('grading_type', 'points'),
            'submission_types': ['online_upload'],
            'submission_types': sub_types, # Uses our variable with the default 'allowed_extensions': post.get('file_types', []),
            'published': PUBLISH,
            'peer_reviews': post.get('peer_reviews', False),
            'automatic_peer_reviews': post.get('automatic_peer_reviews', False),
            'anonymous_peer_reviews': post.get('anonymous_peer_reviews', False),
            'peer_review_count': post.get('peer_review_count', 1)
        }

        # Update or Create
        canvas_assignment = None
        if nice_title in existing_assignments:
            canvas_assignment = existing_assignments[nice_title]
            canvas_assignment.edit(assignment=assignment_data)
        else:
            canvas_assignment = course.create_assignment(assignment=assignment_data)

        # --- 4. RUBRIC ASSOCIATION ---
        if target_rubric != "None" and target_rubric in canvas_rubrics:
            print(f"   -> Attaching Rubric: '{target_rubric}'")
            course.create_rubric_association(rubric_association={
                'rubric_id': canvas_rubrics[target_rubric],
                'association_id': canvas_assignment.id,
                'association_type': 'Assignment',
                'use_for_grading': True,
                'purpose': 'grading'
            })
            # Re-verify points to prevent rubric override
            canvas_assignment.edit(assignment={'points_possible': file_points})

        # --- 5. UPDATE CACHE ---
        cache[md_filename] = current_hash
        save_cache(cache)

if __name__ == "__main__":
    sync_assignments()
