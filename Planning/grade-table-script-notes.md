# Grade Table Script Notes

`generate_grade_table.py` — run from a course directory (the one with `course.yaml`).

## What it does

Reads `course.yaml` for module structure, finds each Assignment and Discussion `.md` file,
pulls `points` and `due_at` from frontmatter, and writes a Markdown table to
`Pages/Syllabus_topics/grade-table.md`.

## Collapse feature

On run, the script asks:

```
Collapse repeated assignments into summary rows? (y/n):
```

If yes, items that share the same base title (after stripping "Week N" and month/date patterns),
type, and per-item points are collapsed into a single summary row:

```
| | Discussion (×10, 20 pts each) | Discussion | | 200 |
```

Collapsed rows appear below unique items, sorted by total points descending.

## Still needs testing / possible tweaks

- `normalize_title()` strips "Week N" and "Month Day" patterns — may need expansion
  if other repetition patterns come up in other courses
- Collapsed rows lose module and due date context (intentional — they span multiple modules)
- Hasn't been fully test-run against every course yet; ENG404 was open when work paused

## File naming convention (established same session)

All `Pages/*.md` and `Pages/Syllabus_topics/*.md` files should be kebab-case:
`reading-calendar.md`, not `Reading_Calendar.md`. Already renamed across all active courses.
`sync_pages.py` matches Canvas pages by H1 title, so renames don't break sync.
