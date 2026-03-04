import os
import csv
import requests
from collections import defaultdict
from config_loader import load_canvas_config, load_course_id

API_URL, API_KEY = load_canvas_config()
API_URL = API_URL.rstrip('/')
COURSE_ID = load_course_id()
CSV_FILE = "Rubrics/rubrics.csv"

def get_existing_rubric_titles(headers):
    """Fetches titles of all rubrics already in the Course Bank."""
    url = f"{API_URL}/api/v1/courses/{COURSE_ID}/rubrics"
    # Handling pagination in case you have a lot of rubrics
    params = {'per_page': 100}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return [r['title'] for r in response.json()]
    return []

def sync_rubrics_explicit():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found.")
        return

    # 1. Fetch current bank
    print("Checking Canvas Rubric Bank for existing titles...")
    existing_titles = get_existing_rubric_titles(headers)

    # 2. Parse CSV (Grouping by the explicit title in every row)
    rubric_groups = defaultdict(list)
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('rubric_title', '').strip()
            if title:
                rubric_groups[title].append(row)

    # 3. Process each group
    for title, rows in rubric_groups.items():
        if title in existing_titles:
            print(f" [SKIPPED] '{title}' already exists.")
            continue

        print(f" [PUSHING] '{title}'...")
        
        # Build payload with Bookmark purpose for the Course Bank
        payload = {
            "rubric[title]": title,
            "rubric_association[association_id]": COURSE_ID,
            "rubric_association[association_type]": "Course",
            "rubric_association[purpose]": "bookmark",
            "rubric_association[use_for_grading]": "false",
        }

        for i, row in enumerate(rows):
            prefix = f"rubric[criteria][{i}]"
            payload[f"{prefix}[description]"] = row.get('criteria_description', 'Criterion')

# ADD THIS LINE:
            payload[f"{prefix}[long_description]"] = row.get('long_description', '').strip()
            
            payload[f"{prefix}[criterion_use_range]"] = "true"            
            ratings = []
            # Dynamically grab rating_1, rating_2, etc.
            rating_cols = [k for k in row.keys() if k.startswith('rating_')]
            for r_col in rating_cols:
                try:
                    idx = r_col.split('_')[1]
                    desc = row.get(r_col, '').strip()
                    pts = row.get(f"pts_{idx}", '').strip()
                    if desc and pts != "":
                        ratings.append({"description": desc, "points": float(pts)})
                except: continue

            # Sort ratings High to Low (Canvas Requirement)
            ratings = sorted(ratings, key=lambda x: x['points'], reverse=True)

            for r_idx, rat in enumerate(ratings):
                r_prefix = f"{prefix}[ratings][{r_idx}]"
                payload[f"{r_prefix}[description]"] = rat["description"]
                payload[f"{r_prefix}[points]"] = rat["points"]

        # 4. Upload
        url = f"{API_URL}/api/v1/courses/{COURSE_ID}/rubrics"
        res = requests.post(url, headers=headers, data=payload)
        
        if res.status_code in [200, 201]:
            print(f"   -> [SUCCESS] Rubric Created.")
        else:
            print(f"   -> [FAILED] {res.status_code}: {res.text}")

if __name__ == "__main__":
    sync_rubrics_explicit()
