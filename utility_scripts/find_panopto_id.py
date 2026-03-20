# Run this once to find your Panopto ID
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from canvasapi import Canvas
from config_loader import load_canvas_config, load_course_id

API_URL, API_KEY = load_canvas_config()
COURSE_ID = load_course_id()

canvas = Canvas(API_URL, API_KEY)
course = canvas.get_course(COURSE_ID)

for tab in course.get_tabs():
    if "Panopto" in tab.label:
        print(f"Label: {tab.label} | ID: {tab.id}")
