### Setting Up A New Course

Here are the basic steps you'll follow to get a project started: 

1. Clone the Repository

2. Copy course_template and rename it for the course you want to develop. We'll call this the course root folder. In the course root folder: 
   
    1. Rename course.yaml.example to course.yaml (Rename the other .yaml files by removing the placeholder .example extension as well.)
    2. Set up your .env file   
        1. Make a copy of .env.example and save it as .env in the canvas-docs-as-code folder. 
        2. Get your Canvas API and save it in .env.
        3. For [Zotero integration](../explanation/zotero-integration.md), get your Zotero API and Zotero ID and save them in .env.
    3. Set the course id. 
        1. Find the course ID for the course you want to sync to. (We recommend syncing to a sandbox course and then importing that course into your live course when everything is ready.)
        2. Save the course ID in the course_id field in course.yaml file (in the root folder for the course). 



3. Set up Python
   
   1. Install Python (if needed).
   2. Create a virtual environment for Python by running `python3 -m venv .venv` in your terminal.
   3. Activate the virtual environment: `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows)
   4. Install dependencies by running `pip install -r requirements.txt` from the project root folder.
   5. Remember to activate your virtual environment before running Python scripts.

