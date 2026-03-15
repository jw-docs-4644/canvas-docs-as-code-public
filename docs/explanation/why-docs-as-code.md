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

# LLMs and Teaching

I believe that we should be very careful when we integrate Large
Language Models (LLMs) into our teaching. Students don't want to read AI
Slop any more than we do, and their slop detectors are just as finely
tuned as ours are. In ethical terms, using AI in this manor fails our
responsibilities to our students. In pragematic terms, we will lose
credibility with our student if they think ChatGPT or Claude has written
our assignments or is providing feedback on their work. Marc Watkins has
a great [substack article on the risks of AI
grading](https://marcwatkins.substack.com/p/the-dangers-of-using-ai-to-grade).

On a much deeper, philosophical level, I believe that we create our
selves through our experiences with the world and with other people.
When we cede important human interactions to machines, we lose the
chance to (re)form ourselves, which to me seems like a great tragedy.

Nevertheless, I do think that LLMs can play a role in course development
that is ethically, pragmatically, and ontologically sound.

## What Role *Should* LLMs Play in Teaching?

Large Language Models are great at working with text, so long as the
work does not require the making of meaning. LLM-based coding agents
combined with a docs-as-code approach to course development enable an
incredible amount of control over course materials.

## Advantages of Automation

Once the "source of truth" for your course lives in the text-based Markdown files on your computer, some of the affordances of working with Large Language Models start to become clear. For example, instead of using a command like

 `find . -type f \( -name '*.md' -o -name '*.yml' -o -name '*.yaml' \) -print0 \
  | xargs -0 sed -i -E 's/(grading_type:[[:space:]]*)letter_grade/\1points/g'`

which would could be used to change the grading type for all of your assignments from letter grade to points, you can simply tell your coding agent something like

`Change the grading type for everything in Assignemnts and Discussions from letter grade to points`

Similarly, if you make changes to an assignment and forget to update the rubric you can ask your coding agent something like

`Review Assignment X and check its rubric. Is everything up to date?`

In my own course prep, I have also found coding agents to be helpful in providing feedback on materials, helping me uncover inconsistencies and assumptions that I had left in prompts because of the blind spots that come from being too close to a topic. 

## The Importance of Context

## Watch Out for Bullshit
