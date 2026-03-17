# Large Language Models and Teaching

I believe that we should be very careful when we integrate Large
Language Models (LLMs) into our teaching. Students don't want to read AI
Slop any more than we do, and their slop detectors are just as finely
tuned as ours are. In ethical terms, using AI in this manner fails our
responsibilities to our students. In pragmatic terms, we will lose
credibility with our students if they think ChatGPT or Claude has written
our assignments or is providing feedback on their work. Marc Watkins has
a great [substack article on the risks of AI
grading](https://marcwatkins.substack.com/p/the-dangers-of-using-ai-to-grade).

On a much deeper, philosophical level, I believe that we create ourselves through our experiences with the world and with other people.
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

which could be used to change the grading type for all of your assignments from letter grade to points, you can simply tell your coding agent something like

`Change the grading type for everything in Assignments and Discussions from letter grade to points`

Similarly, if you make changes to an assignment and forget to update the rubric you can ask your coding agent something like

`Review Assignment X and check its rubric. Is everything up to date?`

In my own course prep, I have also found coding agents to be helpful in providing feedback on materials, helping me uncover inconsistencies and assumptions that I had left in prompts because of the blind spots that come from being too close to a topic. 

## The Importance of the Rhetorical Situation

Any time we engage with Large Language Models, it is important to keep the rhetorical situation in mind. This means reminding yourself and the LLM about purpose, audience, and context on a regular basis. Including contextual cues in prompts and responses helps to keep the writing produced by LLMs anchored in the rhetorical choices of human authors. 

Alan Knowles describes "Human in the Loop" and "Machine in the Loop" writing as different, depending on how much control each side of the scale has over the final product. 

"Machine in the Loop" writing happens when computers assist with writing tasks, but humans are in the driver's seat, making rhetorical choices appropriate to the situation. Writing that is closer to the "Human in the Loop" side of the balance flips the ratio of choice and allows an LLM to create text that tends to disengage itself from the concerns and situations of human beings. This is not the kind of writing that will help us build relationships with our students, and so it will not help their learning. For more on this way of thinking about LLM writing, see [Alan Knowles' 2024 article](https://doi.org/10.1016/j.compcom.2024.102826) in *Computers and Composition*.

## Watch Out for Bullshit

Finally, it is crucial to recognize that Large Language Models do not really care whether the text they produce is factually accurate. 
Hicks et al. [describe ChatGPT specifically as a bullshit machine](https://doi.org/10.1007/s10676-024-09775-5).
I use LLM-coding agents quite a bit in my course prep and other projects, and I can attest to the danger that can arise if we take LLM-generated output as any sort of truth, let alone Truth. 
Luckily, attending to the rhetorical situation provides one mitigation to the bullshit potential of LLMs. As we prepare course materials and teach writing to our students, we should keep this perspective in mind 
