# Extracting a Course

You can use the course extractor to convert an existing course to Markdown and save it to your computer. This can be handy when you're making modifications to an existing course. 

Follow these steps: 

1. Run `python3 extract_course.py`
2. Follow the prompts to find the course you want to extract. 
3. Accept the default folder name and path for the extract or specify a different path if you prefer. 

Results: 

- Assignments, Discussions, Pages, Files, and Rubrics for the course will all be downloaded to the specified path.
- Course settings are saved the course root folder to a file called "course.yaml." 

You can modify these files and re-sync your course content by running `sync_all.sh`