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

SOURCE_DIR = "Discussions"
DEFAULT_POINTS = 20  
PUBLISH = True 
CACHE_FILE = ".sync_cache_discussions.json"

def get_file_hash(data_dict):
    """Creates a unique MD5 hash of the discussion data."""
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
    """Finds the first # H1 in the markdown string."""
    match = re.search(r'^#\s+(.+)$', markdown_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def sync_discussions():
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Folder '{SOURCE_DIR}' not found.")
        return

    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(COURSE_ID)
    cache = load_cache()
    
    print(f"Syncing Graded Discussions for: {course.name}")
    
    canvas_rubrics = {r.title: r.id for r in course.get_rubrics()}
    existing_discussions = {d.title: d for d in course.get_discussion_topics()}

    for md_filename in os.listdir(SOURCE_DIR):
        if not md_filename.endswith('.md'): continue
        
        md_path = os.path.join(SOURCE_DIR, md_filename)
        with open(md_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        # --- 1. TITLE EXTRACTION ---
        nice_title = extract_h1(post.content)
        if not nice_title:
            nice_title = md_filename.replace(".md", "").replace("_", " ").title()

        # --- 2. PREPARE DATA & HASH ---
        file_points = post.get('points', DEFAULT_POINTS)
        target_rubric = post.get('rubric', "None")
        
        check_data = {
            'title': nice_title,
            'points': file_points,
            'rubric': target_rubric,
            'content': post.content,
            'post_first': post.get('post_first', False),
            'discussion_type': post.get('discussion_type', 'threaded'),
            'peer_reviews': post.get('peer_reviews', False)
        }
        current_hash = get_file_hash(check_data)

        # SMART GATEKEEPER
        if cache.get(md_filename) == current_hash and nice_title in existing_discussions:
            print(f"⏩ Skipping: '{nice_title}' (No changes)")
            continue

        # --- 3. PROCESS CONTENT ---
        # Remove the H1 title from the body so it doesn't double-up in Canvas
        body_content = re.sub(r'^#\s+.+$', '', post.content, count=1, flags=re.MULTILINE).strip()

        process = subprocess.run(
            ['pandoc', '-f', 'markdown', '-t', 'html'],
            input=body_content, text=True, capture_output=True, check=True
        )
        html_body = process.stdout

        # --- 4. PAYLOAD CONSTRUCTION ---
        discussion_payload = {
            'title': nice_title,
            'message': html_body,
            'discussion_type': post.get('discussion_type', 'threaded'),
            'type_to_read_replies': post.get('post_first', False), # The "Post First" toggle
            'published': PUBLISH,
            'assignment': {
                'points_possible': file_points,
                'grading_type': 'points',
                'peer_reviews': post.get('peer_reviews', False),
                'automatic_peer_reviews': post.get('automatic_peer_reviews', False),
                'anonymous_peer_reviews': post.get('anonymous_peer_reviews', False),
                'peer_review_count': post.get('peer_review_count', 1)
            }
        }

        # --- 5. SYNC TO CANVAS ---
        current_disc = None
        if nice_title in existing_discussions:
            print(f"🚀 Updating: '{nice_title}'")
            current_disc = existing_discussions[nice_title]
            current_disc.update(**discussion_payload)
        else:
            print(f"✨ Creating: '{nice_title}'")
            current_disc = course.create_discussion_topic(**discussion_payload)

        # --- 6. RUBRIC ASSOCIATION ---
        if target_rubric != "None" and target_rubric in canvas_rubrics:
            # Refresh object to ensure assignment_id is present
            if not hasattr(current_disc, 'assignment_id') or not current_disc.assignment_id:
                current_disc = course.get_discussion_topic(current_disc.id)

            if current_disc.assignment_id:
                print(f"   -> Linking Rubric: '{target_rubric}'")
                course.create_rubric_association(rubric_association={
                    'rubric_id': canvas_rubrics[target_rubric],
                    'association_id': current_disc.assignment_id,
                    'association_type': 'Assignment',
                    'use_for_grading': True,
                    'purpose': 'grading'
                })
                # Re-enforce points
                course.get_assignment(current_disc.assignment_id).edit(assignment={'points_possible': file_points})

        # --- 7. UPDATE CACHE ---
        cache[md_filename] = current_hash
        save_cache(cache)

if __name__ == "__main__":
    sync_discussions()
