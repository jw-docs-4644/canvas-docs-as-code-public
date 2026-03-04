import os
import yaml
import frontmatter
import re

def slugify(text):
    """Converts 'My Discussion 1!' to 'my_discussion_1'"""
    # Convert to lowercase and replace spaces with underscores
    text = text.lower().replace(" ", "_")
    # Remove anything that isn't a letter, number, or underscore
    return re.sub(r'[^a-z0-9_]', '', text)

def rename_course_files(dry_run=True):
    if not os.path.exists("course.yaml"):
        print("❌ course.yaml not found.")
        return

    with open("course.yaml", "r") as f:
        config = yaml.safe_load(f)

    # We will search in both of these directories
    search_dirs = ["Assignments", "Discussions"]
    
    if dry_run:
        print("🧪 DRY RUN MODE: No files will actually be renamed.\n")

    for mod in config.get('modules', []):
        for item in mod.get('items', []):
            if item.get('type') in ['Assignment', 'Discussion']:
                target_title = item.get('title')
                new_filename = f"{slugify(target_title)}.md"
                
                found_current_path = None
                
                # Look in BOTH folders for the file
                for d in search_dirs:
                    if not os.path.exists(d): continue
                    
                    for filename in os.listdir(d):
                        if filename.endswith(".md"):
                            path = os.path.join(d, filename)
                            try:
                                post = frontmatter.load(path)
                                
                                # Get H1 heading
                                file_h1 = ""
                                for line in post.content.split('\n'):
                                    if line.startswith('# '):
                                        file_h1 = line.replace('# ', '').strip()
                                        break
                                
                                # If it matches the title
                                if post.get('title') == target_title or file_h1 == target_title:
                                    found_current_path = path
                                    parent_dir = d
                                    break
                            except:
                                continue
                    if found_current_path: break
                
                if found_current_path:
                    current_filename = os.path.basename(found_current_path)
                    new_path = os.path.join(parent_dir, new_filename)
                    
                    if current_filename == new_filename:
                        print(f"✅ Correct: {parent_dir}/{current_filename}")
                    else:
                        print(f"🔄 Rename: {parent_dir}/{current_filename}  ->  {new_filename}")
                        if not dry_run:
                            os.rename(found_current_path, new_path)
                else:
                    print(f"❌ Missing: No file found for '{target_title}'")

if __name__ == "__main__":
    # Change to False to actually rename the files!
    rename_course_files(dry_run=False)
