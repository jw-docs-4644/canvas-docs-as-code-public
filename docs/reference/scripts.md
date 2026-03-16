# Canvas Scripts Reference

## Sync Scripts

These scripts push content from your local course folders to Canvas.

| Script Name         | Description                                                                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| sync_all.sh         | Bash script that runs all of the python scripts to publish the course                                                                                  |
| sync_assignments.py | Pushes everything from the Assignments folder to Canvas                                                                                                |
| sync_discussions.py | Pushes everything from the Discussions folder to Canvas                                                                                                |
| sync_files.py       | Pushes all of the files in the Files folder to Canvas                                                                                                  |
| sync_pages.py       | Pushes everything from the Pages folder to Canvas                                                                                                      |
| sync_modules.py     | Pushes the organization mapped out in course.yaml to be populated as modules in Canvas.                                                                |
| sync_navigation.py  | Takes the navigation choices set in navigation.yml and builds that navigation in the Canvas course.                                                    |
| sync_rubrics.py     | Checks the csv file in the Rubrics folder and pushes rubrics into the Canvas course.  Refer to the README file in the Rubrics folder for more on this. |

## Utility Scripts

Additional scripts for managing your course:

| Script Name                | Description                                                                                                                                                                                                                                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| nuke_course.py             | This script has the course ID hard coded into it. Run it when you want to reset the content in your course. This can helpful as you work through the course development and want to start with a clean slate in Canvas.                                                                                      |
| extract_course.py          | Pulls an existing course from Canvas, converts it to Markdown, and saves it folders to match the expectations of the sync scripts. This can be helpful if you are working to modify an existing course.                                                                                                        |
| assignment_details_editor.py | Opens a GUI window that lets you edit the due date, point value, and rubric attached to each assignment in the course.  Be careful attaching rubrics! Once a rubric has been attached to an assignment, it can be changed using this tool, but it can only be removed through the Web interface.                |
| resolve_links.py           | Run this script to change relative links in your Markdown files to Canvas-appropriate links in the live course.                                                                                                                                                                                              |
| audit_points.py            | Audits your course structure by checking that points defined in assignment frontmatter match the organization defined in course.yaml.                                                                                                                                                                       |
| check_rubrics.py           | Lists all rubrics currently in your Canvas course with their IDs.                                                                                                                                                                                                                                            |
| validate_frontmatter.py    | Provides shared validation for frontmatter metadata across sync scripts. Issues non-blocking warnings for potential issues (e.g., peer_reviews enabled but peer_review_count too low).                                                                                                                        |
| config_loader.py           | Utility module for loading Canvas configuration from course.yaml or .env files. Handles fallback logic and validation.                                                                                                                                                                                      |
