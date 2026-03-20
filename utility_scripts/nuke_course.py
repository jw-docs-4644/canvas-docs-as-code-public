import os
import sys
import requests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from canvasapi import Canvas
from config_loader import load_canvas_config, load_course_id

# 1. Setup
API_URL, API_KEY = load_canvas_config()
COURSE_ID = load_course_id()

def nuke_course():
    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(COURSE_ID)
    direct_headers = {"Authorization": f"Bearer {API_KEY}"}
    
    print("-" * 40)
    print(f"☢️  TOTAL NUKE INITIATED: {course.name}")
    print("-" * 40)
    
    confirm = input("This will delete EVERYTHING.\nType 'DELETE' to confirm: ")
    if confirm != "DELETE": return

    # --- 1. DELETE MODULES ---
    print("\n🗑️ Deleting Modules...")
    for m in course.get_modules():
        print(f"  - Removing: {m.name}")
        m.delete()

    # --- 2. DELETE RUBRIC ASSOCIATIONS (Corrected Method) ---
    print("\n🔗 Deleting Rubric Associations...")
    # We fetch them via a direct API call because the library attribute is missing
    ra_url = f"{API_URL}/api/v1/courses/{COURSE_ID}/rubric_associations"
    try:
        response = requests.get(ra_url, headers=direct_headers)
        if response.status_code == 200:
            associations = response.json()
            for ra in associations:
                ra_id = ra.get('id')
                print(f"  - Severing Association: {ra_id}")
                requests.delete(f"{ra_url}/{ra_id}", headers=direct_headers)
    except Exception as e:
        print(f"  [SKIPPED] Associations: {e}")

    # --- 3. DELETE ASSIGNMENTS ---
    print("\n📝 Deleting Assignments...")
    for a in course.get_assignments():
        print(f"  - Removing: {a.name}")
        a.delete()

    # --- 4. DELETE DISCUSSIONS ---
    print("\n💬 Deleting Discussions...")
    for d in course.get_discussion_topics():
        print(f"  - Removing: {d.title}")
        d.delete()

    # --- 5. DELETE PAGES ---
    print("\n📄 Deleting Pages...")
    for p in course.get_pages():
        try:
            print(f"  - Removing: {p.url}")
            p.delete()
        except: continue

    # --- 6. DELETE RUBRICS ---
    print("\n💎 Deleting Rubrics...")
    for r in course.get_rubrics():
        try:
            print(f"  - Removing Rubric: {r.title}")
            requests.delete(f"{API_URL}/api/v1/courses/{COURSE_ID}/rubrics/{r.id}", headers=direct_headers)
        except: continue

    # --- 7. DELETE FILES ---
    print("\n📁 Deleting Files...")
    try:
        files = course.get_files()
        for f in files:
            print(f"  - Removing File: {f.display_name}")
            f.delete()
    except Exception as e:
        print(f"  [ERROR] Files: {e}")

    print("\n💥 COURSE WIPE COMPLETE.")

if __name__ == "__main__":
    nuke_course()
