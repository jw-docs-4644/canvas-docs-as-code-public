import os
import yaml
from canvasapi import Canvas
from config_loader import load_canvas_config, load_course_id

# 1. LOAD CONFIGURATION
API_URL, API_KEY = load_canvas_config()
COURSE_ID = load_course_id()

def sync_navigation():
    # Basic Safety Check
    if not API_URL or not API_KEY or not COURSE_ID:
        print("Error: Missing environment variables. Check your .env file.")
        return

    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(COURSE_ID)

    # 2. LOAD CONFIGURATION
    if not os.path.exists("navigation.yaml"):
        print("Error: navigation.yaml not found.")
        return
        
    with open("navigation.yaml", "r") as f:
        try:
            config = yaml.safe_load(f)
        except Exception as e:
            print(f"Error parsing navigation.yaml: {e}")
            return

    # 3. SET HOME PAGE TO MODULES
    # Options: 'feed', 'wiki', 'modules', 'assignments', 'syllabus'
    home_view = config.get('home_page_view', 'modules')
    print(f"🏠 Setting Home Page view to: {home_view}")
    course.update(course={'default_view': home_view})

    # 4. FETCH TABS AND PREPARE SYNC
    canvas_tabs = list(course.get_tabs())
    nav_settings = config.get('navigation', [])
    
    # Map YAML IDs to their intended positions (1-indexed)
    yaml_ids = {item['id']: i for i, item in enumerate(nav_settings, start=1)}

    print("📋 Syncing navigation (Strict Mode)...")

    for tab in canvas_tabs:
        if tab.id in ['home', 'settings']:
            print(f"   [SKIP] {tab.id:<15} (System Protected)")
            continue

        try:
            if tab.id in yaml_ids:
                pos = yaml_ids[tab.id]
                # External tools often need to be explicitly 'unhidden'
                print(f"   [SHOW] {tab.id:<15} | Position: {pos}")
                tab.update(position=pos, hidden=False)
            else:
                # If it's not in our list, hide it.
                # We use a try block because some LTIs are restricted by Admins
                print(f"   [HIDE] {tab.id:<15}")
                tab.update(hidden=True)
                
        except Exception as e:
            # External tools sometimes return a 401 or 400 if the 
            # Developer Key doesn't allow visibility overrides.
            print(f"   [!] Note: Could not modify {tab.id}. This is common for some External Tools.")
            
    print("\n✅ Navigation sync complete.")

if __name__ == "__main__":
    sync_navigation()
