# Multi-Machine Setup

This project uses two repos: a private repo (this one) for daily work, and a public repo for sharing tools. The private repo is the single source of truth. The public repo is a periodic export via `publish.sh`.

## Setting Up a New Machine

### 1. Clone the private repo

```bash
git clone git@github.com:YOUR_USERNAME/canvas-docs-as-code.git
cd canvas-docs-as-code
```

### 2. Set up the Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env` and add your Canvas API URL and API key. These are shared across all courses and are not committed to the repo.

### 4. Set up course configuration

Each course folder (e.g., `ENG_493_1263/`) has its own `course.yaml` with a `course_id` field. If you're starting a new course folder, copy from the template:

```bash
cp course.yaml.example ENG_XXX_XXXX/course.yaml
```

Edit the `course_id` in that file to match your Canvas course.

## Day-to-Day Workflow Across Machines

Pull before you start working:

```bash
git pull
```

Commit and push when you're done:

```bash
git add -A
git commit -m "your message"
git push
```

Everything — scripts, course content, configuration — lives in this one repo. The `.gitignore` keeps credentials and generated files out.

## Publishing to the Public Repo

When you want to update the public repo with your latest tools:

```bash
./publish.sh
```

This uses `rsync` to copy everything except course content (`ENG_*/`), credentials (`.env`), and other private/generated files to the public repo. It shows you `git status` so you can review before committing.

The public repo must already exist. First-time setup:

```bash
git init ../canvas-docs-as-code-public
cd ../canvas-docs-as-code-public
gh repo create canvas-docs-as-code --public --source .
```

After running `publish.sh`, commit and push from the public repo:

```bash
cd ../canvas-docs-as-code-public
git add -A
git commit -m "update tools"
git push
```
