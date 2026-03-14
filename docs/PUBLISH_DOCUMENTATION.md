# publish.sh Documentation Needed

## Bare Bones Outline

**Purpose**: Syncs public-facing files from this repo to a separate public repository, excluding private/generated content.

**Usage**:

```bash
./publish.sh [path-to-public-repo]
```

**Default behavior**: If no path provided, syncs to `../canvas-docs-as-code-public`

**What it does**:

1. Validates the target is a git repo (exits if not)
2. Uses rsync to sync all files with selective exclusions:
   - Excludes: Course folders (ENG_*/), .env files, Python venv, cache files, git/claude metadata, publish.sh itself
   - Deletes files from public repo that no longer exist here
3. Displays git status in public repo for user review
4. Prompts user to manually commit and push when ready

**Setup requirement**: Public repo must be initialized as a git repo first (`git init path/to/public/repo`)

## Topics to document:

- Why this workflow exists (maintain public + private versions in sync)
- How to set up the public repo for the first time
- Full usage examples
- What gets excluded and why
- Manual commit/push requirement (not automated)
