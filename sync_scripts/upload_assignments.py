import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from canvasapi import Canvas
from config_loader import load_canvas_config, load_course_id

# 1. Load your credentials from .env or course.yaml
API_URL, API_KEY = load_canvas_config()
COURSE_ID = load_course_id()

# 2. Connect to Canvas
canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(COURSE_ID)

# 3. Define where your HTML files are
HTML_FOLDER = "Out" 

def main():
    if not os.path.exists(HTML_FOLDER):
        print(f"Error: Folder '{HTML_FOLDER}' not found. Create it and put your HTML files inside.")
        return

    # Get a list of assignments already on Canvas
    print("Fetching current assignments...")
    existing = {a.name: a for a in course.get_assignments()}

    for filename in os.listdir(HTML_FOLDER):
        if filename.endswith(".html"):
            # Turn 'lesson_01.html' into 'Lesson 01'
            title = filename.replace(".html", "").replace("_", " ").title()
            
            with open(os.path.join(HTML_FOLDER, filename), "r") as f:
                html_body = f.read()

            if title in existing:
                print(f"Updating: {title}")
                existing[title].edit(assignment={'description': html_body})
            else:
                print(f"Creating: {title}")
                course.create_assignment({
                    'name': title,
                    'description': html_body,
                    'submission_types': ['online_upload'],
                    'published': False
                })

if __name__ == "__main__":
    main()
