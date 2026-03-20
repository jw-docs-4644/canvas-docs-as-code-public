# Single Sourcing Syllabi

Using a docs-as-code approach for course materials makes it relatively straightforward to take a single-source approach to syllabi. This means that a single source file can be used to generate printed syllabi as well as Canvas pages. Similarly, "boilerplate" and other recycled content can live in a single location. So for example, if your attendance policy is the same in all of your face-to-face classes, you can keep one file in a shared folder that covers this topic and then use it the syllabi for various courses. This explanation covers the basic concepts behind this approach, and how they work in the Canvas Docs as Code Project.

## Topic-Based Authoring

Topic-based authoring is a way of thinking about documentation in terms of the individual topics that might make up a document, instead of thinking about the finished documents themselves. Syllabi present a great example of topic-based authoring, since so much of their content is topical and re-used across multiple courses. 

The following table outlines a few possible topics for a syllabus, as well as whether each topic might be thought of as *shared* across multiple courses or *unique* to a specific course. (Naturally, whether a topic is unique will depend on a variety of factors. For example, if I'm teaching multiple sections of the same course, then Course Outcomes might be shared. If not, then they'll probably be unique.)

| Topic | Shared or Unique |
| ----- | ---------------- |
| Course Name | Unique |
| Meeting Place and Time | Unique |
| Instructor Name and Contact Info | Shared |
| Course Outcomes | Unique |
| Attendance Policy | Shared |
| Grading Policy | Shared |
| Drafts and Revisions | Shared |
| Reading Calendar | Unique |

Hopefully this small set of examples makes it clear how beneficial it can be think of syllabi in terms of topics. If I decide to make a change to my attendance policy, I can do that once and let that topic be used to generate consistent syllabi for all of my relevant classes. 

The syllabus is created by using [pandoc and a default file written in yaml](../how-to/how-to-use-pandoc-and-yaml.md). 

## Single Source, Multiple Outputs

Another thing we can do with syllabus topics is to push some or all of them to individual Canvas pages. For example, I use the same approach to drafts and revisions in all of my classes, and I like to have that information in a "Getting Started" module on Canvas. I can use the course.yaml file to grab whichever topics I choose from my syllabus folders and put them in that module.

The extra columns in the table below suggests a possible set of outputs for our hypothetical syllabus topics:

| Topic | Shared or Unique | Send to Syllabus | Send to Canvas |
| ----- | ---------------- | ---------------- | -------------- |
| Course Name | Unique | Yes | Yes |
| Meeting Place and Time | Unique | Yes | Yes |
| Instructor Name and Contact Info | Shared | Yes | No |
| Course Outcomes | Unique | Yes | Yes |
| Attendance Policy | Shared | Yes | Yes |
| Grading Policy | Shared | Yes | No |
| Drafts and Revisions | Shared | Yes | Yes |
| Reading Calendar | Unique | Yes | Yes |

Topics are added to the modules page by putting them in the course.yaml file in the course root folder.

## Topic Locations

The default structure of the Canvas Docs as Code Project assumes the following locations for syllabus and Canvas topics:

- Shared topics: canvas-docs-as-code/_shared/syllabus/topics
- Course-specific topics: [course root folder]/Pages/Syllabus_topics

If you want to store topics in other locations, you will need to update your course.yaml file and perhaps make adjustments to the sync_pages.py script. 

## Conclusion

Clearly this will require more organization and set up time than it would take to just write a syllabus in Word. But once the organizational structure has been worked out, it will be much easier to keep syllabi consistent and up to date across courses. 
