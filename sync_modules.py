import os
import yaml
from canvasapi import Canvas
from config_loader import load_canvas_config, load_course_id

API_URL, API_KEY = load_canvas_config()
COURSE_ID = load_course_id()

def sync_modules():
    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(COURSE_ID)
    
    with open("course.yaml", "r") as f:
        config = yaml.safe_load(f)

    print("Indexing course content...")

    content_map = {
        'Assignment': {a.name: a.id for a in course.get_assignments()},
        'Discussion': {d.title: getattr(d, 'assignment_id', d.id) for d in course.get_discussion_topics()},
        'Page': {p.title: {'id': p.page_id, 'url': p.url} for p in course.get_pages()},
        'Quiz': {q.title: q.id for q in course.get_quizzes()}
    }

    existing_modules = {m.name: m for m in course.get_modules()}

    for mod_cfg in config.get('modules', []):
        mod_name = mod_cfg['name']
        
        # Ensure new modules are created as published
        module = existing_modules.get(mod_name) or course.create_module(module={'name': mod_name, 'published': True})
        
        # Sync module publication status from YAML
        is_pub = mod_cfg.get('published', True) # Defaulting to True for convenience
        if module.published != is_pub:
            module.edit(module={'published': is_pub})

        canvas_items = {item.title: item for item in module.get_module_items()}
        yaml_item_titles = [i.get('title') for i in mod_cfg.get('items', []) if isinstance(i, dict) and i.get('title')]

        # 1. CLEANUP
        for title, item in canvas_items.items():
            if title not in yaml_item_titles:
                print(f"  [-] Removing: {title}")
                item.delete()

        # 2. SYNC
        for item_cfg in mod_cfg.get('items', []):
            if not isinstance(item_cfg, dict): continue
            title = item_cfg.get('title')
            ctype = item_cfg.get('type')
            
            if not title or not ctype:
                continue
            
            indent = item_cfg.get('indent', 0)
            
            # --- UPDATE EXISTING ITEMS ---
            if title in canvas_items:
                target_item = canvas_items[title]
                # Force publish if it's currently unpublished
                if target_item.indent != indent or not getattr(target_item, 'published', True):
                    print(f"  [*] Updating: {title} (Publishing/Indenting)")
                    target_item.edit(module_item={'indent': indent, 'published': True})
                continue

            # --- PREPARE DATA FOR NEW ITEMS ---
            # We add 'published': True here so all new items are live immediately
            item_data = {'title': title, 'indent': indent, 'published': True}

            if ctype == "SubHeader":
                item_data['type'] = 'SubHeader'
            elif ctype == "ExternalUrl":
                item_data['type'] = 'ExternalUrl'
                item_data['external_url'] = item_cfg.get('url')
                item_data['new_tab'] = True
            else:
                canvas_type = 'Assignment' if ctype == 'Assignment' else \
                              'DiscussionTopic' if ctype == 'Discussion' else \
                              'Quiz' if ctype == 'Quiz' else 'WikiPage'
                item_data['type'] = canvas_type

                found = None
                for cat in content_map.values():
                    if title in cat:
                        found = cat[title]
                        break

                if not found:
                    print(f"  [!] Skip: '{title}' not found in Canvas.")
                    continue

                if canvas_type == 'WikiPage':
                    item_data['content_id'] = found['id']
                    item_data['page_url'] = found['url']
                else:
                    item_data['content_id'] = found

            # --- EXECUTE CREATE ---
            try:
                print(f"  [+] Adding & Publishing {ctype}: {title}")
                module.create_module_item(module_item=item_data)
            except Exception as e:
                if ctype == "Discussion":
                    try:
                        item_data['type'] = 'Assignment'
                        module.create_module_item(module_item=item_data)
                        print(f"    [*] Fixed: {title} linked as Assignment.")
                    except:
                        print(f"    [!] Failed {title}: {e}")
                else:
                    print(f"    [!] Failed {title}: {e}")

    print("\n✅ Sync Finished.")

if __name__ == "__main__":
    sync_modules()
