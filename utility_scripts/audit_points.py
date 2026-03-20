import os
import yaml
import frontmatter
import re
from tabulate import tabulate

def slugify(text):
    text = text.lower().replace(" ", "_")
    return re.sub(r'[^a-z0-9_]', '', text)

def audit_points():
    if not os.path.exists("course.yaml"):
        print("❌ Error: course.yaml not found!")
        return

    with open("course.yaml", "r") as f:
        config = yaml.safe_load(f)

    table_data = []
    total_points = 0

    print("--- STARTING DEBUG SCAN ---")
    
    # Check if 'modules' even exists
    if 'modules' not in config:
        print("❌ Error: No 'modules' key found in course.yaml!")
        return

    for mod in config.get('modules', []):
        mod_name = mod.get('name', 'Untitled')
        print(f"Checking Module: {mod_name}")
        
        for item in mod.get('items', []):
            title = item.get('title', 'NO TITLE')
            # Use .lower() here to prevent "Discussion" vs "discussion" errors
            item_type = str(item.get('type')).lower()
            
            print(f"  > Found Item: '{title}' [Type: {item_type}]")

            if "assignment" in item_type or "discussion" in item_type:
                clean_name = f"{slugify(title)}.md"
                
                # Auto-detect folder based on type
                folder = "Assignments" if "assignment" in item_type else "Discussions"
                file_path = os.path.join(folder, clean_name)
                
                points = 0
                status = "❓ Missing"

                if os.path.exists(file_path):
                    post = frontmatter.load(file_path)
                    val = post.get('points') or post.get('Points')
                    if val is not None:
                        points = float(val)
                        total_points += points
                        status = "✅ OK"
                    else:
                        status = "⚠️ No 'points' key in file"
                else:
                    # Let's see exactly where it looked
                    status = f"❌ File not at: {file_path}"

                table_data.append([item_type.capitalize(), title, points, status])

    print("\n--- FINAL SUMMARY ---")
    headers = ["Type", "Title", "Points", "Status"]
    print(tabulate(table_data, headers=headers, tablefmt="outline"))
    print(f"\nTOTAL POINTS: {total_points}")

if __name__ == "__main__":
    audit_points()
