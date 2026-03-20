import os
import re
from canvasapi import Canvas
from config_loader import load_canvas_config, load_course_id

# --- SETUP ---
API_URL, API_KEY = load_canvas_config()
API_URL = API_URL.rstrip('/')
COURSE_ID = load_course_id()

class LinkResolver:
    def __init__(self):
        self.canvas = Canvas(API_URL, API_KEY)
        self.course = self.canvas.get_course(COURSE_ID)
        
        # Universal pattern: catches anything inside href or src quotes
        self.link_pattern = re.compile(r'(?:href|src)=["\']([^"\']+)["\']', re.IGNORECASE)
        
        self.broken_links = [] 
        self.success_count = 0  # NEW: Success tracker
        self.id_map = self._build_id_map()

    def _to_slug(self, text):
        if not text: return ""
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        return text.strip('-')

    def _build_id_map(self):
        print("Building Canvas ID Map...")
        id_map = {}
        for page in self.course.get_pages():
            slug = page.url
            id_map[f"pages/{slug}"] = f"/courses/{COURSE_ID}/pages/{slug}"
            id_map[f"pages/{re.sub(r'-\d+$', '', slug)}"] = f"/courses/{COURSE_ID}/pages/{slug}"
        for assign in self.course.get_assignments():
            slug = self._to_slug(assign.name)
            id_map[f"assignments/{slug}"] = f"/courses/{COURSE_ID}/assignments/{assign.id}"
        for disc in self.course.get_discussion_topics():
            slug = self._to_slug(disc.title)
            id_map[f"discussions/{slug}"] = f"/courses/{COURSE_ID}/discussion_topics/{disc.id}"
        for f in self.course.get_files():
            name_parts = f.display_name.rsplit('.', 1)
            raw_name = name_parts[0]
            ext = name_parts[1].lower() if len(name_parts) > 1 else ""
            slug_name = self._to_slug(raw_name)
            key = f"files/{slug_name}.{ext}" if ext else f"files/{slug_name}"
            id_map[key] = f"/courses/{COURSE_ID}/files/{f.id}/download?wrap=1"

        # Add filename-slug aliases for local content directories.
        # Links in markdown files use filenames (e.g. Final_Project.md), but Canvas
        # titles may have extra words (e.g. "Final Project: Major Audio Composition").
        # This indexes each file by its filename slug so both resolve correctly.
        for content_dir, content_type in [("Assignments", "assignments"), ("Pages", "pages"), ("Discussions", "discussions")]:
            if not os.path.exists(content_dir):
                continue
            for dirpath, _, filenames in os.walk(content_dir):
                for fname in filenames:
                    if not fname.endswith('.md'):
                        continue
                    file_slug = self._to_slug(fname[:-3])  # strip .md
                    alias_key = f"{content_type}/{file_slug}"
                    if alias_key in id_map:
                        continue  # already mapped exactly, no alias needed
                    filepath = os.path.join(dirpath, fname)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as fh:
                            content = fh.read()
                        m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                        if m:
                            title_slug = self._to_slug(m.group(1).strip())
                            title_key = f"{content_type}/{title_slug}"
                            if title_key in id_map:
                                id_map[alias_key] = id_map[title_key]
                    except Exception:
                        pass

        return id_map

    def resolve_html(self, html, container_name):
        def replacer(match):
            original_path = match.group(1)
            
            # 1. THE NEGATIVE LOOKAHEAD FILTER
            # Ignores external links, mailto, and internal anchors
            if original_path.startswith(('http', 'https', 'mailto', '#')):
                return match.group(0)

            # 2. NORMALIZATION
            filename = os.path.basename(original_path)
            name_parts = filename.rsplit('.', 1)
            raw_name = name_parts[0]
            ext = name_parts[1].lower() if len(name_parts) > 1 else ""
            
            slug_name = self._to_slug(raw_name)
            file_key = f"files/{slug_name}.{ext}" if ext else f"files/{slug_name}"
            attr = match.group(0).split('=')[0] 
            
            # 3. ATTEMPT MATCHING
            # Try Files
            if file_key in self.id_map:
                self.success_count += 1
                return f'{attr}="{self.id_map[file_key]}"'
            
            # Try Content
            keys_to_check = [f"assignments/{slug_name}", f"pages/{slug_name}", f"discussions/{slug_name}"]
            for key in keys_to_check:
                if key in self.id_map:
                    self.success_count += 1
                    return f'{attr}="{self.id_map[key]}"'
            
            # 4. LOG FAILURE
            self.broken_links.append({'container': container_name, 'link': original_path})
            return match.group(0)

        return self.link_pattern.sub(replacer, html)

    def process_and_upload(self, dry_run=True):
        print("\nStarting Rossum's Universal Link Resolver...")
        # (Processing Pages, Assignments, Discussions)
        items_processed = 0
        for p_sum in self.course.get_pages():
            p = self.course.get_page(p_sum.url)
            if p.body:
                new_html = self.resolve_html(p.body, f"Page: {p.title}")
                if p.body != new_html and not dry_run: p.edit(wiki_page={'body': new_html})
            items_processed += 1
        for a in self.course.get_assignments():
            if a.description:
                new_html = self.resolve_html(a.description, f"Assignment: {a.name}")
                if a.description != new_html and not dry_run: a.edit(assignment={'description': new_html})
            items_processed += 1
        for d in self.course.get_discussion_topics():
            if d.message:
                new_html = self.resolve_html(d.message, f"Discussion: {d.title}")
                if d.message != new_html and not dry_run: d.edit(discussion_topic={'message': new_html})
            items_processed += 1

        self.print_report(items_processed)

    def print_report(self, items_processed):
        print("\n" + "="*75)
        print(" FINAL LINK RESOLUTION REPORT")
        print("="*75)
        print(f"Items Scanned:  {items_processed}")
        print(f"Links Fixed:    {self.success_count} ✅")
        print(f"Broken Links:   {len(self.broken_links)} ⚠️")
        
        if self.broken_links:
            print("\nDETAILS ON BROKEN LINKS:")
            current_container = ""
            for item in sorted(self.broken_links, key=lambda x: x['container']):
                if item['container'] != current_container:
                    print(f"\n📍 In {item['container']}:")
                    current_container = item['container']
                print(f"   - '{item['link']}'")
        print("\n" + "="*75)

if __name__ == "__main__":
    resolver = LinkResolver()
    resolver.process_and_upload(dry_run=False)
