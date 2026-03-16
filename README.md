# Canvas Docs as Code

Full documentation: at [doc-design.dev](https://www.doc-design.dev)

## Background

The goal of this project is to be able to write an entire Canvas course using plain text editors to the greatest extent possible. It arose as I was redesigning my Advanced Technical Course to focus more on topic-based and structured authoring, with a heavy emphasis on writing in Markdown. Early in that process, I thought, "Wouldn't it be great if I could just push my course into Canvas and never have to click the mouse?" I stumbled across the Canvas API, and after asking ChatGPT to help me understand Python and write the code, I was able to push a single HTML page to Canvas. 

From there I was hooked, and with a great deal of help from ChatGPT, Gemini, and finally the Claude Coding Tool, I was able to build a set of scripts that makes it possible to write and push 99% of a  Canvas course from the terminal, with only a few final tweaks happening in in the Canvas Web interface after the course has been built.    

## How It Works

This project lets you develop your course materials in plain text files on your local machine and then push them to your Canvas site using the Canvas API. Here's the basic workflow: 

- Assignments, Discussions, and Pages
   - You write your assignment prompts, discussion prompts, and course pages in Markdown, using any editor you like. 
   - You provide metadata such as grading type and points values  at the top of each item using YAML (Yet Another Markup Language) fields. 
- Rubrics
   - You write your rubrics in a spreadsheet program, using CSV (comma separated values). You *can* to this in a text editor, but I found it much easier to use a spreadsheet.
- Modules and Course Settings
   - You write another YAML file to organize the modules for your class. 
   - Yet another YAML file determines the settings. 

You run the python scripts in this repository to push all of your content into Canvas.

### Prerequisites

Here's what you'll need to make this work: 

- A basic knowledge of how python works, or a willingness to muddle through. 
- A similar level of knowledge or attitude about git and Github.
- A willingness to learn Markdown and yaml. 

## The Scripts

See the [Scripts Reference](docs/reference/scripts.md) for a complete list of available scripts and their purposes. 

## Course Development Workflow

1. Write your content.
- Assignments, Discussions, and Pages: Check the Markdown template in each folder for the required structure of the Markdown and the YAML metadata.

- Rubrics: Be sure to read the [How to Use Rubrics](docs/how-to/using-rubrics.md) and follow the template guidelines.

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
## Why do this?

My motivations for the project are three-fold: 

1. Because it was an interesting project. 
2. Because it helped me learn about Markdown for a class where I'd be teaching a lot of Markdown.
3. Because I hate mousing around in Canvas. 

And anyways, I think it's kind of cool!

