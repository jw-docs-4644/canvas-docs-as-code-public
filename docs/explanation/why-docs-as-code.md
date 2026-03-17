# Why Docs-as-Code for Canvas?

Docs as Code is an approach to technical documentation that asks writers to use the same tools and processes that software developers use. 

## Why Treat Documentation as Code?

Treating documentation like code lets the documentation work fit more cleanly into the development process. When documentation is built using the same tools as the software it supports, it integrated more easily into the system.

# Docs as Code and Course Development

Applying a docs-as-code philosophy
to course development unlocks the power of plain text and gives you much more control over your course than you'd get using traditional development tools.

The scripts in the canvas-docs-as-code-public repository let you write your course on your local machine, create due dates, assign points values, set peer review options, and
then push all of your content to Canvas with a single command. The publish script will also check for broken links, and update links to match the course you
are pushing to.

Since everything lives in just a few folders on your computer, it is much easier to make global changes. For example, all of the rubrics are kept in a single CSV spreadsheet. If you decide to change a feedback
term from "Unsatisfactory" to "Needs Significant Development" all it takes is a single Find & Replace.

# Docs-as-Code Tools

Docs as Code uses different kinds of tools than are usually found in
"traditional" documentation systems. This table offers a comparison of
some of the more commonly used tools:

| Purpose           | Docs-as-Code Tools                                                                        | Traditional Documentation Tools                                          |
| ----------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Document Creation | Plain-text editors such as Gedit or Micro or Markdown editors such as Typedown or Ulysses | Word processors such as Microsoft Word, OpenOffice, or even Google Docs. |
| Version Control   | Git, Subversion                                                                           | File syncing services such as OneDrive, Google Drive, or Dropbox.        |
| Automation        | Scripting Languages such as Python or LLM tools such as Cluade CLI                        | Macros in Word or OpenOffice.                                            |

# Docs as Code and LLM Coding Agents

Once LLM-based Coding Agents enter the picture, the docs-as-code
approach reveals its true potential. Now instead of simply updating a
term in your rubrics, you can make changes to an assignment, then ask
the coding agent to check the rubric for consistency. Or you can have
the coding agent change all of your discussion prompts from pass/fail to
graded by points.

