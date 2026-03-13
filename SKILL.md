 # Skill metadata (required)
  name: build-presentation
  description: Analyzes specified files to create a MD file that can be converted to PPT and docx.  (Claude uses this to auto-trigger)

  # Optional configuration
  disable-model-invocation: false    # Set to true for side-effects (deploy, commit)
  user-invocable: true                # Set to false for background reference only
  #argument-hint: "[file-path]"        # Show expected arguments in autocomplete
  allowed-tools: Read, Grep, Edit     # Comma-separated tools allowed without prompting
  # context: fork                     # Uncomment to run in isolated subagent
  # agent: Explore                    # If context: fork, use Explore/Plan/general-purpose
  # model: sonnet                     # Override model for this skill
  ---

  # Build Presentation

  ## Purpose
  This skill is used to analyze PDFs, notes, and course documents to write a MD file and convert it to PPT and docx. 

  ## Instructions

  When this skill is invoked:

  1. **First step**: Read through the specified filed or prompt the user is none have been specified. 
  2. **Second step**: Read the PDFs to gain context. Then read the notes. The notes are my highlights from the PDFs. Some will contain instructions regarding how what I want on the presentation. Some will be just highlighted sections from the PDFs. It is okay to infer structure from slides where it is specified for slides where it is not. 
  3. **Third Step**: Write a md file that uses hashtags for headings. Level 1 headings are for section breaks, and cannot contain content, but can contain speakers notes (see below). Level 2 headings create new slides and can contain content. Bulleted lists are preferred, but not required. Content should be shortened as needed to fit into a maximum of 8 lines of text. The comments will indicate that some material should go in speakers notes. Speakers notes should be fenced between ::: notes and ::: (Each fence goes on its own line, with the speakers notes between the fences. If material is not flagged specifically for slide content, it is okay to decide whether to put it in speakers notes. 
  4. **Fourth Step** Check relevant readings and course activities in the Assignments and Discussions folders for connections. If clear and helpful connections can be made to the assignments, discussions, or readings from the course, add them to the speaker's notes.  
  5. **Fifth Step** Save the MD file in the directory where the skill was invoked. Then run "pandoc [input.md] -o [output.pptx] -t pptx --reference-doc=/home/josh/Documents/PPT_Template.pptx --slide-level=2 & pandoc [input.md] --lua-filter=../no-notes.lua -o [output.docx]. If you can't find the PPT_Template.pptx and/or no-notes.lua, look in nearby project folderes or prompt the user for the location. 

  ## Key behaviors

  - Always use MLA-style citations for any quoted material. Double check page numbers. Do not infer or guess. If you can't be sure, write page not found in the MLA citation. 
  - If the notes call for images, download images from the web and resize them to work well in the formats we'll be using. Include an MLA-style citation for images whenever possible. Store images in a subfolder called `images`, which you are allowed to create if missing. 
  - Never use emoticons. 
  - Focus on the sections I notes that indicated sections I've highlighted in the PDFs. These will help shape the presentation. 

  ## Example usage

  If the user runs `/build-presentation`, do the steps outlined above. Prompt the user for files or context that can help. Multiple choice prompts are preferred. .

  ## Notes

  Feel free to ask for more input from the user if you think it will help make a more authentic presentation. 
