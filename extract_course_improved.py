import os
import csv
import requests
import frontmatter
import subprocess
import yaml
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from canvasapi import Canvas

load_dotenv()
API_URL = os.getenv("CANVAS_API_URL")
API_KEY = os.getenv("CANVAS_API_KEY")

# Target extensions
DOC_EXTS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf'}
IMG_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp'}
ALLOWED_EXTENSIONS = DOC_EXTS.union(IMG_EXTS)

def html_to_md(html_content):
    if not html_content: return ""
    try:
        process = subprocess.run(
            ['pandoc', '-f', 'html', '-t', 'gfm'],
            input=html_content, text=True, capture_output=True, check=True
        )
        return process.stdout
    except Exception: return html_content

def sanitize(name):
    if not name: return "unnamed_item"
    return "".join([c for c in name if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')

def format_term_display(term_name):
    match = re.search(r'(\d{4})', term_name)
    if match:
        year = match.group(1)
        rest = term_name.replace(year, "").strip()
        return f"{year} {rest}"
    return term_name

def select_course(canvas):
    print("📡 Fetching your courses from Canvas...")
    courses = list(canvas.get_courses(enrollment_type='teacher', include=['term']))
    
    groups = {}
    for c in courses:
        code = getattr(c, 'course_code', 'UNKNOWN')
        group_key = code[:6].strip().upper()
        if group_key not in groups: groups[group_key] = []
        groups[group_key].append(c)

    unique_groups = sorted(groups.keys())
    print("\n--- [STEP 1] Select Course Group ---")
    for i, g in enumerate(unique_groups, 1):
        print(f"[{i}] {g} ({len(groups[g])} versions)")
    
    grp_idx = int(input("\nEnter Group Number: ")) - 1
    selected_group_key = unique_groups[grp_idx]
    group_courses = groups[selected_group_key]

    terms_map = {}
    for c in group_courses:
        term_info = getattr(c, 'term', {})
        term_name = term_info.get('name', 'Default Term')
        term_id = term_info.get('id', 0)
        display_label = format_term_display(term_name)
        key = (term_id, display_label)
        if key not in terms_map: terms_map[key] = []
        terms_map[key].append(c)

    sorted_term_keys = sorted(terms_map.keys(), key=lambda x: x[0])
    print(f"\n--- [STEP 2] Select Term for {selected_group_key} ---")
    for i, (t_id, t_display) in enumerate(sorted_term_keys, 1):
        print(f"[{i}] {t_display}")
    
    term_idx = int(input("\nEnter Term Number: ")) - 1
    selected_term_key = sorted_term_keys[term_idx]

    term_courses = terms_map[selected_term_key]
    if len(term_courses) > 1:
        print(f"\n--- [STEP 3] Select Specific Section ---")
        for i, c in enumerate(term_courses, 1):
            print(f"[{i}] {c.name} (Code: {c.course_code})")
        c_idx = int(input("\nEnter Course Number: ")) - 1
        return term_courses[c_idx]
    
    return term_courses[0]

def extract_all():
    canvas = Canvas(API_URL, API_KEY)
    course = select_course(canvas)

    print(f"\n🏗️  INITIATING EXTRACTION: {course.name}")

    # Ask user where to extract
    default_folder = sanitize(f"{course.course_code}_{course.name}")
    print(f"\n--- [OUTPUT LOCATION] ---")
    print(f"[1] Use default folder: {default_folder}")
    print(f"[2] Specify custom path")

    location_choice = input("\nChoose option [1-2]: ").strip()

    if location_choice == "2":
        custom_path = input("Enter a path for extraction: ").strip()
        base_path = Path(custom_path)
    else:
        base_path = Path(default_folder)

    print(f"📁 Extracting to: {base_path.absolute()}")

    for sub in ['Assignments', 'Pages', 'Discussions', 'Files']:
        (base_path / sub).mkdir(parents=True, exist_ok=True)

    # 1. Rubrics
    print("\n💎 Step 1: Processing Rubrics...")
    csv_file = base_path / 'rubrics.csv'
    headers = ['rubric_title', 'criteria_description', 'long_description', 'rating_1', 'pts_1', 'rating_2', 'pts_2', 'rating_3', 'pts_3', 'rating_4', 'pts_4', 'rating_5', 'pts_5']

    # Check if rubrics.csv already exists
    file_exists = csv_file.exists()
    all_assignments = list(course.get_assignments())
    seen_rubrics = set()

    # If file exists, read existing rubrics to avoid duplicates
    if file_exists:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            for row in reader:
                if row:  # Only process non-empty rows
                    seen_rubrics.add(row[0])  # Track by rubric title
        write_mode = 'a'  # Append
        print(f"   ℹ️  Appending to existing rubrics.csv")
    else:
        write_mode = 'w'  # Create new

    with open(csv_file, write_mode, newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)  # Only write header if creating new file
        for a in all_assignments:
            if hasattr(a, 'rubric'):
                r_id = a.rubric_settings.get('title')
                if r_id and r_id not in seen_rubrics:
                    seen_rubrics.add(r_id)
                    for crit in a.rubric:
                        row = [a.rubric_settings.get('title'), crit.get('description'), crit.get('long_description')]
                        ratings = crit.get('ratings', [])
                        for i in range(5):
                            if i < len(ratings): row.extend([ratings[i].get('description'), ratings[i].get('points')])
                            else: row.extend(['', ''])
                        writer.writerow(row)

    # 2. Content
    print("\n📥 Step 2: Extracting Assignments, Pages, and Discussions...")
    for a in all_assignments:
        md = html_to_md(getattr(a, 'description', ''))
        post = frontmatter.Post(
            f"# {a.name}\n\n{md}",
            points=getattr(a, 'points_possible', 0),
            grading_type=getattr(a, 'grading_type', 'points')
        )
        with open(base_path / 'Assignments' / f"{sanitize(a.name)}.md", 'wb') as f:
            frontmatter.dump(post, f)

    for p in course.get_pages():
        full_p = course.get_page(p.url)
        md = html_to_md(getattr(full_p, 'body', ''))
        post = frontmatter.Post(f"# {full_p.title}\n\n{md}", title=full_p.title)
        with open(base_path / 'Pages' / f"{sanitize(full_p.title)}.md", 'wb') as f:
            frontmatter.dump(post, f)

    for d in course.get_discussion_topics():
        md = html_to_md(getattr(d, 'message', ''))
        post = frontmatter.Post(f"# {d.title}\n\n{md}", published=d.published)
        with open(base_path / 'Discussions' / f"{sanitize(d.title)}.md", 'wb') as f:
            frontmatter.dump(post, f)

    # 3. Filtered Files
    print("\n📁 Step 3: Downloading PDFs, Documents, and Images...")
    files = list(course.get_files())
    for file in files:
        ext = Path(file.display_name).suffix.lower()
        if ext in ALLOWED_EXTENSIONS:
            f_path = base_path / 'Files' / sanitize(file.display_name)
            if not f_path.exists():
                print(f"   -> Downloading: {file.display_name}")
                try:
                    r = requests.get(file.url, headers={'Authorization': f'Bearer {API_KEY}'}, timeout=10)
                    with open(f_path, 'wb') as f: f.write(r.content)
                except: print(f"      [!] Failed to download: {file.display_name}")
        else:
            print(f"   -- Skipping non-target file type: {file.display_name}")

    # 4. Modules
    print("\n📦 Step 4: Building Module Map...")
    course_yaml_file = base_path / 'course.yaml'

    # Preserve existing course_id if it exists
    existing_course_id = None
    if course_yaml_file.exists():
        try:
            with open(course_yaml_file, 'r', encoding='utf-8') as f:
                existing_data = yaml.safe_load(f)
                if existing_data and 'course_id' in existing_data:
                    existing_course_id = existing_data['course_id']
                    print(f"   ℹ️  Found existing course_id: {existing_course_id}")
        except Exception as e:
            print(f"   [!] Could not read existing course.yaml: {e}")

    # Build course_map with course_id first (if it exists)
    course_map = {}
    if existing_course_id:
        course_map['course_id'] = existing_course_id

    course_map['course_name'] = course.name
    course_map['modules'] = []

    for mod in course.get_modules():
        print(f"   -> Mapping Module: {mod.name}")
        m_data = {'name': mod.name, 'items': []}
        for item in mod.get_module_items():
            m_data['items'].append({'title': item.title, 'type': item.type})
        course_map['modules'].append(m_data)

    # Check if course.yaml already exists
    if course_yaml_file.exists():
        print(f"\n   ⚠️  course.yaml already exists in this folder")
        merge_choice = input("   [1] Overwrite with extracted modules (preserving course_id)\n   [2] Keep existing course.yaml\n   Choose [1-2]: ").strip()
        if merge_choice == "2":
            print(f"   ℹ️  Keeping existing course.yaml")
        else:
            with open(course_yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(course_map, f, sort_keys=False, allow_unicode=True)
            print(f"   ✓ Updated course.yaml with extracted modules")
    else:
        with open(course_yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(course_map, f, sort_keys=False, allow_unicode=True)

    print(f"\n✅ SUCCESS: Full backup created in {base_path.absolute()}")
    sys.exit(0)

if __name__ == "__main__":
    extract_all()
