#!/bin/bash

TARGET_FOLDERS=("Assignments" "Discussions" "Pages" "Files")

for folder in "${TARGET_FOLDERS[@]}"; do
    if [ ! -d "$folder" ]; then continue; fi
    
    find "$folder" -maxdepth 1 -name "*.md" | while read -r filepath; do
        dir=$(dirname "$filepath")
        filename=$(basename "$filepath")
        extension="${filename##*.}"
        name="${filename%.*}"

        # Standardizing logic
        new_name=$(echo "$name" | tr '[:upper:]' '[:lower:]' | \
                   sed -e 's/[[:space:]_]/-/g' \
                       -e 's/[^a-z0-9-]//g' \
                       -e 's/-\{2,\}/-/g' \
                       -e 's/^-//' -e 's/-$//')
        
        new_filename="${new_name}.${extension}"

        if [ "$filename" != "$new_filename" ]; then
            # --- THIS IS THE DRY RUN LINE ---
            git mv "$dir/$filename" "$dir/$new_filename"
        fi
    done
done
