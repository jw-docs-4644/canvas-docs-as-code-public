# Docs as Code and Course Development

Applying a [docs-as-code](explanation-about-docs-as-code.md) philosophy to course development unlocks the power of plain text and gives you much more control over your course than you'd get using traditional development tools. 

The scripts in this repository let you write your course on your local machine, create due dates, points values, and peer review settings, and then push all of your content to Canvas with a single command. They will also check for broken links, and update links to match the course you are pushing to. 

Since everything lives in just a few folders on your computer, it is much easier to make global changes. For example, all of the rubrics are kept in a single CSV spreadsheet. If you decide to change a feedback term from "Unsatisfactory" to "Needs Significant Development" all it takes is a single Find & Replace. 

## Docs as Code and LLM Coding Agents

Once LLM-based Coding Agents enter the picture, the docs-as-code approach reveals its true potential. Now instead of simply updating a term in your rubrics, you can make changes to an assignment, then ask the coding agent to check the rubric for consistency. Or you can have the coding agent change all of your discussion prompts from pass/fail to graded by points. 
