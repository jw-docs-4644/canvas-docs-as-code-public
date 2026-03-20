# Use Pandoc and yaml to Generate Syllabi. 

!! This is under deverlopment!!!

I'm working out a way for syllabus topics to be single sources and used in multiple places. It turned out to be more complicated than I thought. But I think I got it figured out. 

- Root folder contains a subfolder called _shared/syllabus/topics
- In this folder live topics that you want to use in more than one class. 

- your class folder has a folder called ?Pages/Syllabus_topics
- In this folder live MD files with course-specific information: Course OUtcomes, Reading Calendars, etc. 

-course.yaml
    -This builds the modules layout for canvas. It pulls pages and lists them. It assumes that pages are in Pages or a subfolder.
    - You can tell it to look in _shared/syllabus/topics by listing source: shared inside  the item block (See structure in sample course.yaml.)

the logic for this has been updated in sync_pages.py

-defaults-yaml (or maybe we give it a better name? ) can be used to build printed syllabi. These can pull from the shared topics as well as Pages. It lives in course root/Syllabus