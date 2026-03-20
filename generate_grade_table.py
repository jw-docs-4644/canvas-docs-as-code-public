"""
generate_grade_table.py

Run from a course directory (the one containing course.yaml).
Reads course.yaml for module structure, then reads each Assignment and
Discussion .md file to collect title, due date, and points.

Writes a Markdown table to Pages/Syllabus_topics/grade-table.md.

When prompted, you can choose to collapse repeated assignment types
(e.g. all weekly discussions, all lecture reflections) into a single
summary row showing the count and total points.
"""

import os
import re
import sys
import yaml
import frontmatter

MONTHS = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
)


def slugify(text):
    text = text.lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_]", "", text)


def extract_h1(content):
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def find_file(title, folder):
    """Try slugified filename; fall back to scanning folder for matching H1."""
    slug = slugify(title) + ".md"
    path = os.path.join(folder, slug)
    if os.path.exists(path):
        return path

    # Fallback: scan folder for a file whose H1 matches the title
    if os.path.isdir(folder):
        for fname in os.listdir(folder):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(folder, fname)
            post = frontmatter.load(fpath)
            if extract_h1(post.content) == title:
                return fpath

    return None


def normalize_title(title):
    """Strip week numbers and dates to find a repeating assignment's base name."""
    # Remove "Week N" with optional surrounding punctuation/spaces
    title = re.sub(r'\bWeek\s+\d+\b[\s,:-]*', '', title, flags=re.IGNORECASE)
    # Remove "Month Day" date patterns (e.g. "April 7", "January 15")
    month_pat = '|'.join(MONTHS)
    title = re.sub(rf'\b({month_pat})\s+\d+\b[\s,:-]*', '', title, flags=re.IGNORECASE)
    # Remove leading/trailing punctuation and collapse whitespace
    title = re.sub(r'^[\s,:-]+|[\s,:-]+$', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip()


def fmt_pts(pts):
    if pts == "":
        return ""
    f = float(pts)
    return int(f) if f == int(f) else f


def collapse_rows(rows):
    """
    Split rows into unique items and groups of repeated items.

    Returns (unique_rows, collapsed_rows) where:
      unique_rows: list of original (mod, title, type, due, pts) tuples
      collapsed_rows: list of (base_title, type, count, total_pts) tuples
    """
    from collections import defaultdict

    # Group by (normalized_title, type, points_per_item)
    groups = defaultdict(list)
    for row in rows:
        mod, title, itype, due, pts = row
        key = (normalize_title(title), itype, pts)
        groups[key].append(row)

    unique_rows = []
    collapsed_rows = []

    for key, group_rows in groups.items():
        base_title, itype, pts_each = key
        if len(group_rows) == 1:
            unique_rows.append(group_rows[0])
        else:
            count = len(group_rows)
            total = float(pts_each) * count if pts_each != "" else ""
            collapsed_rows.append((base_title or itype, itype, count, total, pts_each))

    # Restore original order for unique rows
    order = {id(r): i for i, r in enumerate(rows)}
    unique_rows.sort(key=lambda r: order[id(r)])

    return unique_rows, collapsed_rows


def generate_grade_table():
    if not os.path.exists("course.yaml"):
        print("Error: course.yaml not found. Run from a course directory.")
        sys.exit(1)

    with open("course.yaml") as f:
        config = yaml.safe_load(f)

    rows = []

    for mod in config.get("modules", []):
        mod_name = mod.get("name", "Untitled")
        for item in mod.get("items", []):
            item_type = str(item.get("type", "")).lower()
            if item_type not in ("assignment", "discussion"):
                continue

            title = item.get("title", "")
            folder = "Assignments" if item_type == "assignment" else "Discussions"
            fpath = find_file(title, folder)

            points = ""
            due_at = ""

            if fpath:
                post = frontmatter.load(fpath)
                h1 = extract_h1(post.content)
                if h1:
                    title = h1
                val = post.get("points") or post.get("Points")
                if val is not None:
                    points = int(val) if float(val) == int(float(val)) else float(val)
                due = post.get("due_at")
                if due:
                    due_at = str(due)

            rows.append((mod_name, title, item_type.capitalize(), due_at, points))

    # Ask about collapsing
    answer = input("Collapse repeated assignments into summary rows? (y/n): ").strip().lower()
    collapse = answer == "y"

    if collapse:
        unique_rows, collapsed_rows = collapse_rows(rows)
    else:
        unique_rows = rows
        collapsed_rows = []

    # Build markdown table
    lines = [
        "---",
        "title: Grade Table",
        "---",
        "",
        "# Grade Table",
        "",
        "| Module | Assignment | Type | Due | Points |",
        "| --- | --- | --- | --- | --- |",
    ]
    total = 0

    for mod_name, title, itype, due, pts in unique_rows:
        lines.append(f"| {mod_name} | {title} | {itype} | {due} | {fmt_pts(pts)} |")
        if pts != "":
            total += float(pts)

    if collapsed_rows:
        lines.append("| | | | | |")
        for base_title, itype, count, total_pts, pts_each in sorted(collapsed_rows, key=lambda r: -float(r[3] or 0)):
            pts_each_fmt = fmt_pts(pts_each)
            total_pts_fmt = fmt_pts(total_pts)
            label = f"{base_title} (×{count}, {pts_each_fmt} pts each)"
            lines.append(f"| | {label} | {itype} | | {total_pts_fmt} |")
            if total_pts != "":
                total += float(total_pts)

    lines.append(f"| | | | **Total** | **{fmt_pts(total)}** |")
    lines.append("")

    out_dir = os.path.join("Pages", "Syllabus_topics")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "grade-table.md")

    with open(out_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Written to {out_path}")
    print(f"Total points: {fmt_pts(total)}")


if __name__ == "__main__":
    generate_grade_table()
