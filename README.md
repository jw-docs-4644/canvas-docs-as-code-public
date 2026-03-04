# Canvas Docs as Code

## Background

The goal of this project is to be able to write an entire Canvas course using plain text editors to the greatest extent possible. It arose as I was redesigning my Advanced Technical Course to focus more on topic-based and structured authoring, with a heavy emphasis on writing in Markdown. Early in that process, I thought, "Wouldn't it be great if I could just push my course into Canvas and never have to click the mouse?" I stumled across the Canvas API, and after asking ChatGPT to help me understand Python and write the code, I was able to push a single HTML page to Canvas. 

From there I was hooked, and with a great deal of help from ChatGPT, Gemini, and finally the Claude Coding Tool, I was able to build a set of scripts that makes it possible to write and push 99% of a  Canvas course from the terminal, with only a few final tweaks happening in in the Canvas Web interface after the course has been built.    

## Why do this?

My motivations for the project are three-fold: 

1. Because it was an interesting project. 
2. Because it helped me learn about Markdown for a class where I'd be teaching a lot of Markdown.
3. Because I hate mousing around in Canvas. 

And anwyays, I think it's kind of cool!

## How It Works

The basic idea is this:

- You write your assignment prompts, discusion prompts, and course pages in Markdown, using any editor you like. 
- You provide metadata such as grading type and points values  at the top of each item using YAML (Yet Anaother Markup Language) fields. 
- You write your rubrics in a spreadheet program, using CSV (comma separated values). You *can* to this in a text editor, but I found it much easier to use a spreadsheet.
- You write another YAML file to organize the modules for your class. 
- Yet another YAML file determines the settings. 

You run python scripts to push all of your content into Canvas. 

### Prerequisites

Here's what you'll need to make this work: 

- A basic knowledge of how python works, or a willingess to muddle through. 
- A similar level of knowledge or antitude about git and Github.
- A willingness to learn Markdown.  

### Setup

Here are the basic steps you'll follow to get a project started: 

1. Clone the Repository

2. Set up your .env file
   
   1. Copy .env.example to .env
   2. Get your Canvas API and save it in  .env

3. Copy course_template and rename it for the course you want to develop. In the new folder: 
   
   1. Rename course.yaml.example to course.yaml
      
      Rename the other .yaml files by remvoing the placeholder .example extenstion as well. 

4. Set up Python
   
   1. Install Python (if needed)
   
   2. Install dependencies by opening a terminal and running `pip install -r requirements.txt` from the project root folder. 
   
   3. Set up your course folder
   
   4. Make a copy of the course_template folder and rename it for your course.
      Your course folder should include the following sub-folders: 
      
      - Assignments
      - Discussions
      - Pages
      - Files

### Configuration

* Configure the .env to store your Canvas API key and Canvas url. 

* Configure the course.yaml file for in each course folder with the relevant course ID number from Canvas.  

<!-- Need to figure out how to handle course-specific ID numbers for individual courses within the Repo. -->

## The Scripts

Hopefully  the script names are pretty clear, but just in case my lack of python experience makes things confusing, I've included a table of the scripts and what they are intended to do. 

### Sync Scripts

Most of the scripts take the files in the course folders and push them to Canvas. 

| Script Name         | Description                                                                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| sync_all.sh         | Bash script that runs all of the python scripts to publish the course                                                                                  |
| sync_assignments.py | Pushes everything from the Assignments folder to Canvas                                                                                                |
| sync_discussions.py | Pushes everything form the Discussions folder to Canvas                                                                                                |
| sync_files.py       | Pushes all of the files in the Files folder to Canvas                                                                                                  |
| sync_pages.py       | Pushes everything from the Pages folder to Canvas                                                                                                      |
| sync_modules.py     | Pushes the organization mapped out in course.yaml to be populated as modules in Canvas.                                                                |
| sync_navigation.py  | Takes the navigation choices set in navigation.yml and builds that navigation in the Canvas course.                                                    |
| sync_rubrics.py     | Checks the csv file in the Rubrics folder and pushes rubrics into the Canvas course.  Refer to the README file in the Rubrics folder for more on this. |

### Utility Scripts

In addition to the main content-pushing scripts described above, there are several scripts that are useful when using this system to build your course:

| Script Name                                           | Description                                                                                                                                                                                                                                                                                                  |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| nuke_course.py                                        | This script has the course ID hard coded into it. Run it when you want to reset the content in your course. This can helpful as you work through the course development and want to start with a clean slate in Canvas.                                                                                      |
| extract_full_course.py and extract_course_improved.py | These two scripts both pull an existing course from Canvas, convert it to Markdown, and save it folders to match the expectations of the sync scripts. This can be helpful if you are working to modify an existing course.  The differences between the scripts involve the way the course is selected.     |
| points_editor.py                                      | This script opens a GUI window that lets you edit the due date, point value, and rubric attached to each assignment in the course.  Be careful attaching rubrics! Once a rubric has been attached to an assignment, it can be changed using this tool, but it can only be removed through the Web interface. |
| resolve_links.py                                      | Run this script to change relative links in your Markdown files to Canvas-appropriate links in the live course.                                                                                                                                                                                              |

## Course Development Workflow

1. Write your content.
- Assignments, Discussions, and Pages: Check the Markdown template in each folder for the required structure of the Markdown and the YAML metadata.

- Rubrics: Be sure to read the README in the rubrics folder and follow the template guidelines.

- If you use modules, modify course.yaml to organize them. Refer to course.yaml.example for help with this. (More documentation on this coming soon!)
2. (Optional) Configure navigation and defaults:
   Copy navigation.yml.example and defaults.yaml.example to set Canvas navigation tab order and Pandoc build settings for exporting a standalone PDF/HTML version of the course. (More documentation soon!)

3. Deploy to Canvas
     Run bash sync_all.sh from inside your course folder. This runs all the sync scripts in order (rubrics → assignments →
     discussions → pages → files → modules → navigation → link resolution and pushes everything to Canvas via the API.
     Double check and manually fix any unresolved links in Canvas afterward.
- Settings that still need to be set in Canvas: 
  (Coming soon)

## Project Structure

## Contributing
