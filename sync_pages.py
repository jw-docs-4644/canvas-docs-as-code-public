import os
import subprocess
import frontmatter
import re
import json
import hashlib
import yaml
from canvasapi import Canvas
from config_loader import load_canvas_config, load_course_id

# 1. Setup
API_URL, API_KEY = load_canvas_config()
COURSE_ID = load_course_id()

SOURCE_DIR = "Pages"
PUBLISH = True
CACHE_FILE = ".sync_cache_pages.json"

# Path to shared syllabus topics, relative to this script's location
SHARED_TOPICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_shared", "syllabus", "topics")

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

def get_shared_pages():
    """Read course.yaml and return list of shared pages.
    Each entry is a dict with 'title' and optional 'file' (explicit filename in _shared/).
    If 'file' is provided, that file is used and pushed to Canvas under 'title'.
    If not, the file is looked up by matching 'title' against H1 headings in _shared/.
    """
    if not os.path.exists("course.yaml"):
        return []
    with open("course.yaml", 'r') as f:
        config = yaml.safe_load(f)
    shared = []
    seen = set()
    for module in config.get('modules', []):
        for item in module.get('items', []):
            if item.get('source') == 'shared' and item.get('type') == 'Page':
                title = item['title']
                if title not in seen:
                    seen.add(title)
                    shared.append({'title': title, 'file': item.get('file')})
    return shared

def build_shared_map():
    """Scan _shared/syllabus/topics/ and return {title: filepath}."""
    title_map = {}
    if not os.path.exists(SHARED_TOPICS_DIR):
        print(f"[!] Shared topics directory not found: {SHARED_TOPICS_DIR}")
        return title_map
    for filename in os.listdir(SHARED_TOPICS_DIR):
        if not filename.endswith('.md'):
            continue
        filepath = os.path.join(SHARED_TOPICS_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            title = extract_h1(content)
            if title:
                title_map[title] = filepath
        except Exception:
            pass
    return title_map

def sync_file(md_path, cache_key, existing_pages, cache, course, title_override=None):
    """Convert a markdown file to HTML and create or update the Canvas page.
    title_override: if set, use this as the Canvas page title instead of the H1.
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
    except Exception as e:
        print(f"[!] YAML ERROR in '{cache_key}': {e}")
        return

    nice_title = title_override or extract_h1(post.content) or cache_key

    check_data = {
        'title': nice_title,
        'content': post.content,
        'published': post.get('published', PUBLISH),
        'front_page': post.get('front_page', False)
    }
    current_hash = get_file_hash(check_data)

    if cache.get(cache_key) == current_hash and nice_title in existing_pages:
        print(f"⏩ Skipping: '{nice_title}' (No changes)")
        return

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

    if nice_title in existing_pages:
        print(f"🚀 Updating Page: '{nice_title}'")
        existing_pages[nice_title].edit(wiki_page=page_data)
    else:
        print(f"✨ Creating Page: '{nice_title}'")
        course.create_page(wiki_page=page_data)

    cache[cache_key] = current_hash
    save_cache(cache)

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

    # 1. Sync course-specific pages from Pages/ (recursively)
    for dirpath, _, filenames in os.walk(SOURCE_DIR):
        for md_filename in filenames:
            if not md_filename.endswith('.md'):
                continue
            md_path = os.path.join(dirpath, md_filename)
            cache_key = os.path.relpath(md_path, SOURCE_DIR)
            sync_file(md_path, cache_key, existing_pages, cache, course)

    # 2. Sync shared pages from _shared/syllabus/topics/
    shared_pages = get_shared_pages()
    if shared_pages:
        shared_map = build_shared_map()
        for page in shared_pages:
            title = page['title']
            explicit_file = page.get('file')

            if explicit_file:
                # Direct filename lookup — push to Canvas under the course.yaml title
                filepath = os.path.join(SHARED_TOPICS_DIR, explicit_file)
                if not os.path.exists(filepath):
                    print(f"[!] Shared file '{explicit_file}' not found in {SHARED_TOPICS_DIR}")
                    continue
                cache_key = f"shared/{explicit_file}"
                sync_file(filepath, cache_key, existing_pages, cache, course, title_override=title)
            else:
                # Title-based lookup — H1 in the shared file must match course.yaml title
                if title not in shared_map:
                    print(f"[!] Shared topic '{title}' not found in {SHARED_TOPICS_DIR}")
                    continue
                filepath = shared_map[title]
                cache_key = f"shared/{os.path.basename(filepath)}"
                sync_file(filepath, cache_key, existing_pages, cache, course)

if __name__ == "__main__":
    sync_pages()
