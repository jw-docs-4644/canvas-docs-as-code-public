# Using Rubrics

All the rubrics for a course are stored in rubrics.csv, which lives in the root folder for the course. To set up rubrics for your course, follow these steps: 

1. Open rubrics.csv, but do not change the headings for each column in row 1.
2. Fill in the a cell for each of the assessment criteria you want the rubric to contain. Note that the rubric title must be repeated on every row and cannot be left blank. The sync script creates a new rubric whenever a new rubric title appears.
3. Name the rubric by title in the yaml metadata for the assignment or discussion. For example, `rubric: Analytical Essay`  will look for a the phrase Analytical Essay in the rubric_title field. 
4. Set rubric_use_for_grading to true or false. Use true if you want the rubric to generate a grade when you fill it out in Canvas. Use false for peer review or other formative purposes where you want to use the rubric to provide feedback to the student, but not generate a the grade for the activity. 

When you push your content to Canvas, the sync scripts will look in rubrics.csv to build the rubrics and then check the assignment/discussion metadata to make associations. 

Tip: It can be helpful to edit the rubrics in a program like OpenOfffice or Excel so that formulas and formatting persist. Just be sure to save changes to rubrics.csv---that's the file that is used to send rubrics to Canvas.  
