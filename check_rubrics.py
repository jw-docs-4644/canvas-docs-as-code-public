from canvasapi import Canvas
from config_loader import load_canvas_config, load_course_id

API_URL, API_KEY = load_canvas_config()
COURSE_ID = load_course_id()

canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(COURSE_ID)

rubrics = course.get_rubrics()
for r in rubrics:
    print(f"ID: {r.id} | Title: {r.title}")
