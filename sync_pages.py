import os
import subprocess
import frontmatter
import re
import json
import hashlib
from canvasapi import Canvas
from config_loader import load_canvas_config, load_course_id

# 1. Setup
API_URL, API_KEY = load_canvas_config()
COURSE_ID = load_course_id()

SOURCE_DIR = "Pages" 
PUBLISH = True
CACHE_FILE = ".sync_cache_pages.json"

def get_file_hash(data_dict):
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
    match = re.search(r'^#\s+(.+)$', markdown_text, re.MULTILINE)
    return match.group(1).strip() if match else None

def sync_pages():
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Folder '{SOURCE_DIR}' not found.")
        return

    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(COURSE_ID)
    cache = load_cache()
    
    print(f"Syncing Pages for: {course.name}")
    
    # MATCH BY TITLE: This is much more reliable than guessing slugs
    existing_pages = {p.title: p for p in course.get_pages()}

    for md_filename in os.listdir(SOURCE_DIR):
        if not md_filename.endswith('.md'): continue
        
        md_path = os.path.join(SOURCE_DIR, md_filename)
        
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
        except Exception as e:
            print(f"[!] YAML ERROR in '{md_filename}': {e}")
            continue

        # 1. Extract Info
        nice_title = extract_h1(post.content) or md_filename.replace(".md", "").title()
        
        # 2. Smart Hash Check
        check_data = {
            'title': nice_title,
            'content': post.content,
            'published': post.get('published', PUBLISH),
            'front_page': post.get('front_page', False)
        }
        current_hash = get_file_hash(check_data)

        if cache.get(md_filename) == current_hash and nice_title in existing_pages:
            print(f"⏩ Skipping: '{nice_title}' (No changes)")
            continue

        # 3. Process Body (Remove H1)
        body_content = re.sub(r'^#\s+.+$', '', post.content, count=1, flags=re.MULTILINE).strip()
        process = subprocess.run(
            ['pandoc', '-f', 'markdown', '-t', 'html'],
            input=body_content, text=True, capture_output=True, check=True
        )
        html_body = process.stdout

        page_data = {
            'title': nice_title,
            'body': html_body,
            'published': post.get('published', PUBLISH),
            'front_page': post.get('front_page', False)
        }

        # 4. Create or Update using Title Matching
        if nice_title in existing_pages:
            print(f"🚀 Updating Page: '{nice_title}'")
            existing_pages[nice_title].edit(wiki_page=page_data)
        else:
            print(f"✨ Creating Page: '{nice_title}'")
            course.create_page(wiki_page=page_data)

        # 5. Update Cache
        cache[md_filename] = current_hash
        save_cache(cache)

if __name__ == "__main__":
    sync_pages()
