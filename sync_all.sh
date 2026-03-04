# sync_all.sh
python3 sync_rubrics.py
python3 sync_assignments.py
python3 sync_discussions.py
python3 sync_pages.py
python3 sync_files.py
python3 sync_modules.py
python3 sync_navigation.py
python3 resolve_links.py
echo "Deployment complete, but you will need to go into Canvas to fix the links that couldn't be resolved."
