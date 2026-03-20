import json
import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import xml.etree.ElementTree as ET
import yaml
import zipfile

SUPPORTED_EXTENSIONS = {".md", ".docx", ".dita"}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LUA_FILTER_PATH = os.path.join(SCRIPT_DIR, "newpage-h1.lua")
CSS_SIDEBAR_PATH = os.path.join(SCRIPT_DIR, "toc-sidebar.css")

FORMAT_OPTIONS = ["pdf", "html", "docx", "epub", "odt", "latex"]
FORMAT_EXTENSIONS = {
    "pdf":   ".pdf",
    "html":  ".html",
    "docx":  ".docx",
    "epub":  ".epub",
    "odt":   ".odt",
    "latex": ".tex",
}
FORMAT_FILETYPES = {
    "pdf":   [("PDF files", "*.pdf")],
    "html":  [("HTML files", "*.html")],
    "docx":  [("Word documents", "*.docx")],
    "epub":  [("EPUB files", "*.epub")],
    "odt":   [("OpenDocument Text", "*.odt")],
    "latex": [("LaTeX files", "*.tex")],
}

# Windows-1252 C1 control characters that Word embeds and XeLaTeX cannot render.
# Map them to their proper Unicode equivalents before parsing pandoc's JSON AST.
_C1_MAP = str.maketrans({
    '\u0091': '\u2018',  # left single quotation mark
    '\u0092': '\u2019',  # right single quotation mark
    '\u0093': '\u201c',  # left double quotation mark
    '\u0094': '\u201d',  # right double quotation mark
    '\u0095': '\u2022',  # bullet
    '\u0096': '\u2013',  # en dash
    '\u0097': '\u2014',  # em dash
})

_title_cache = {}

def get_file_title(path):
	if path in _title_cache:
		return _title_cache[path]
	title = _extract_title(path)
	_title_cache[path] = title
	return title

def _extract_title(path):
	ext = os.path.splitext(path)[1].lower()
	try:
		if ext == ".md":
			return _md_title(path)
		elif ext == ".docx":
			return _docx_title(path)
		elif ext == ".dita":
			return _dita_title(path)
	except Exception:
		pass
	return os.path.basename(path)

def _md_title(path):
	with open(path, encoding="utf-8", errors="ignore") as f:
		in_frontmatter = None
		for line in f:
			stripped = line.strip()
			if in_frontmatter is None:
				if stripped == "---":
					in_frontmatter = True
					continue
				else:
					in_frontmatter = False
			if in_frontmatter and stripped in ("---", "..."):
				in_frontmatter = False
				continue
			if in_frontmatter:
				continue
			if stripped.startswith("# "):
				title = stripped[2:].strip()
				title = title.strip("*_")
				return title
	return os.path.basename(path)

def _docx_title(path):
	ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
	heading_ids = {"Heading1", "heading1", "Titre1", "berschrift1"}
	with zipfile.ZipFile(path) as z:
		with z.open("word/document.xml") as f:
			tree = ET.parse(f)
	for para in tree.findall(f".//{{{ns}}}p"):
		style_el = para.find(f".//{{{ns}}}pStyle")
		if style_el is not None:
			val = style_el.get(f"{{{ns}}}val", "")
			if val in heading_ids:
				texts = para.findall(f".//{{{ns}}}t")
				title = "".join(t.text or "" for t in texts).strip()
				if title:
					return title
	return os.path.basename(path)

def _dita_title(path):
	tree = ET.parse(path)
	title_el = tree.getroot().find("title")
	if title_el is not None and title_el.text:
		return title_el.text.strip()
	return os.path.basename(path)


class DragDropTreeview(ttk.Treeview):
	def __init__(self, master, **kwargs):
		super().__init__(master, **kwargs)
		self._drag_item = None
		self.bind("<ButtonPress-1>", self._on_press)
		self.bind("<B1-Motion>", self._on_drag)
		self.bind("<ButtonRelease-1>", self._on_release)

	def _on_press(self, event):
		col = self.identify_column(event.x)
		item = self.identify_row(event.y)
		if col == "#1" and item and hasattr(self, "toggle_callback"):
			self.toggle_callback(item)
			return "break"
		self._drag_item = item

	def _on_drag(self, event):
		if not self._drag_item:
			return
		target = self.identify_row(event.y)
		if not target or target == self._drag_item:
			return
		parent = self.parent(self._drag_item)
		self.move(self._drag_item, parent, self.index(target))

	def _on_release(self, event):
		self._drag_item = None


class MapMakerApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Pandoc MapMaker")

		self.abs_paths = []
		self.enabled_paths = set()
		self._geometry_file = os.path.expanduser("~/.mapmaker_geometry")
		self._build_ui()
		self._load_geometry()
		self.root.protocol("WM_DELETE_WINDOW", self._on_close)

	def _build_ui(self):
		main = ttk.Frame(self.root, padding=10)
		main.pack(fill=tk.BOTH, expand=True)

		# File list
		self.tree = DragDropTreeview(
			main,
			columns=("enabled", "filename", "path"),
			show="headings",
			height=15
		)
		self.tree.heading("enabled", text="✓")
		self.tree.heading("filename", text="Title")
		self.tree.heading("path", text="Folder")
		self.tree.column("enabled", width=30, anchor="center", stretch=False)
		self.tree.column("filename", width=340)
		self.tree.column("path", width=280)
		self.tree.toggle_callback = self._toggle_enabled

		scroll = ttk.Scrollbar(main, orient="vertical", command=self.tree.yview)
		self.tree.configure(yscrollcommand=scroll.set)

		self.tree.grid(row=0, column=0, sticky="nsew")
		scroll.grid(row=0, column=1, sticky="ns")

		main.rowconfigure(0, weight=1)
		main.columnconfigure(0, weight=1)

		# Buttons
		btn_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
		btn_frame.pack(fill=tk.X)

		ttk.Button(btn_frame, text="Load YAML", command=self.load_yaml).pack(side=tk.LEFT)
		ttk.Separator(btn_frame, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=8)
		ttk.Button(btn_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT)
		ttk.Button(btn_frame, text="Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=5)
		ttk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT)
		ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
		ttk.Separator(btn_frame, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=8)
		ttk.Button(btn_frame, text="Select All", command=self._select_all).pack(side=tk.LEFT)
		ttk.Button(btn_frame, text="Deselect All", command=self._deselect_all).pack(side=tk.LEFT, padx=5)
		ttk.Separator(btn_frame, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=8)
		ttk.Button(btn_frame, text="▲ Move Up", command=self.move_up).pack(side=tk.LEFT)
		ttk.Button(btn_frame, text="▼ Move Down", command=self.move_down).pack(side=tk.LEFT, padx=5)

		# Pandoc Options Panel
		options = ttk.LabelFrame(self.root, text="Pandoc Options", padding=10)
		options.pack(fill=tk.X, padx=10, pady=5)

		# Output format
		ttk.Label(options, text="Output Format:").grid(row=0, column=0, sticky="w")
		self.format_var = tk.StringVar(value="pdf")
		format_dropdown = ttk.Combobox(
			options,
			textvariable=self.format_var,
			values=FORMAT_OPTIONS,
			state="readonly",
			width=10,
		)
		format_dropdown.grid(row=0, column=1, sticky="w")
		format_dropdown.bind("<<ComboboxSelected>>", self._on_format_change)

		# PDF Engine (PDF-only)
		self._engine_label = ttk.Label(options, text="PDF Engine:")
		self._engine_label.grid(row=0, column=2, sticky="w", padx=(20, 4))
		self.engine_var = tk.StringVar(value="xelatex")
		self._engine_dropdown = ttk.Combobox(
			options,
			textvariable=self.engine_var,
			values=["xelatex", "lualatex", "pdflatex"],
			state="readonly",
			width=10,
		)
		self._engine_dropdown.grid(row=0, column=3, sticky="w")

		# TOC
		self.toc_var = tk.BooleanVar(value=True)
		ttk.Checkbutton(options, text="Include TOC", variable=self.toc_var).grid(row=1, column=0, sticky="w")

		# Number sections
		self.number_var = tk.BooleanVar(value=True)
		ttk.Checkbutton(options, text="Number Sections", variable=self.number_var).grid(row=1, column=1, sticky="w")

		# New page before H1 (PDF-only)
		self.new_page_var = tk.BooleanVar(value=False)
		self._new_page_cb = ttk.Checkbutton(
			options, text="New page before each H1", variable=self.new_page_var
		)
		self._new_page_cb.grid(row=1, column=2, columnspan=2, sticky="w", padx=(20, 0))

		# Sidebar TOC (HTML-only)
		self.sidebar_toc_var = tk.BooleanVar(value=False)
		self._sidebar_toc_cb = ttk.Checkbutton(
			options, text="Sidebar TOC", variable=self.sidebar_toc_var
		)
		self._sidebar_toc_cb.grid(row=1, column=2, columnspan=2, sticky="w", padx=(20, 0))
		self._sidebar_toc_cb.grid_remove()  # hidden by default (PDF is default format)

		# TOC Depth
		ttk.Label(options, text="TOC Depth:").grid(row=1, column=4, sticky="w", padx=(20, 4))
		self.toc_depth_var = tk.IntVar(value=3)
		ttk.Spinbox(options, textvariable=self.toc_depth_var, from_=1, to=6, width=3).grid(row=1, column=5, sticky="w")

		# Title
		ttk.Label(options, text="Title:").grid(row=2, column=0, sticky="w")
		self.title_var = tk.StringVar(value="ENG 404 Recipe Book")
		ttk.Entry(options, textvariable=self.title_var, width=40).grid(row=2, column=1, columnspan=3, sticky="w")

		# Author
		ttk.Label(options, text="Author:").grid(row=3, column=0, sticky="w")
		self.author_var = tk.StringVar(value="Winter 2026")
		ttk.Entry(options, textvariable=self.author_var, width=40).grid(row=3, column=1, columnspan=3, sticky="w")

		# Output file
		ttk.Label(options, text="Output File:").grid(row=4, column=0, sticky="w", pady=(8, 0))
		output_frame = ttk.Frame(options)
		output_frame.grid(row=4, column=1, columnspan=3, sticky="ew", pady=(8, 0))
		self.output_var = tk.StringVar()
		ttk.Entry(output_frame, textvariable=self.output_var, width=34).pack(side=tk.LEFT)
		ttk.Button(output_frame, text="Browse…", command=self.browse_output).pack(side=tk.LEFT, padx=(4, 0))

		# Bottom buttons + status
		bottom = ttk.Frame(self.root, padding=(10, 0, 10, 10))
		bottom.pack(fill=tk.X)

		ttk.Button(bottom, text="Save Pandoc Defaults YAML", command=self.save_yaml).pack(side=tk.LEFT)
		self.run_btn = ttk.Button(bottom, text="▶ Run Pandoc", command=self.run_pandoc)
		self.run_btn.pack(side=tk.LEFT, padx=10)
		self.cancel_btn = ttk.Button(bottom, text="✕ Cancel", command=self._cancel_pandoc)
		self.cancel_btn.pack(side=tk.LEFT)
		self.cancel_btn.pack_forget()

		self.status_var = tk.StringVar(value="")
		ttk.Label(bottom, textvariable=self.status_var, foreground="gray").pack(side=tk.LEFT)

		# Log panel
		log_frame = ttk.LabelFrame(self.root, text="Log", padding=5)
		log_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

		self.log_text = tk.Text(
			log_frame, height=6, wrap=tk.WORD, state="disabled",
			font=("Courier", 9), background="#1e1e1e", foreground="#d4d4d4",
		)
		log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
		self.log_text.configure(yscrollcommand=log_scroll.set)
		self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

	def _on_format_change(self, _event=None):
		is_pdf = self.format_var.get() == "pdf"
		is_html = self.format_var.get() == "html"
		state = "readonly" if is_pdf else "disabled"
		self._engine_dropdown.configure(state=state)
		self._engine_label.configure(foreground="" if is_pdf else "gray")
		self._new_page_cb.configure(state="normal" if is_pdf else "disabled")
		if is_html:
			self._new_page_cb.grid_remove()
			self._sidebar_toc_cb.grid()
		else:
			self._sidebar_toc_cb.grid_remove()
			self._new_page_cb.grid()
		current = self.output_var.get().strip()
		if current:
			base = os.path.splitext(current)[0]
			self.output_var.set(base + FORMAT_EXTENSIONS.get(self.format_var.get(), ""))

	def _load_geometry(self):
		try:
			with open(self._geometry_file) as f:
				geometry = f.read().strip()
			self.root.geometry(geometry)
		except (FileNotFoundError, tk.TclError):
			pass

	def _on_close(self):
		try:
			with open(self._geometry_file, "w") as f:
				f.write(self.root.geometry())
		except OSError:
			pass
		self.root.destroy()

	def load_yaml(self):
		load_path = filedialog.askopenfilename(
			filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
		)
		if not load_path:
			return

		with open(load_path, "r", encoding="utf-8") as f:
			data = yaml.safe_load(f)

		if not data or "input-files" not in data:
			messagebox.showwarning("Load YAML", "No 'input-files' key found in that YAML.")
			return

		base_dir = os.path.dirname(load_path)

		# Restore options if present
		if "to" in data:
			self.format_var.set(data["to"])
			self._on_format_change()
		if "pdf-engine" in data:
			self.engine_var.set(data["pdf-engine"])
		self.toc_var.set(bool(data.get("toc", False)))
		self.number_var.set(bool(data.get("number-sections", False)))
		filters = data.get("filters") or []
		self.new_page_var.set("newpage-h1.lua" in filters)
		css_files = data.get("css") or []
		self.sidebar_toc_var.set("toc-sidebar.css" in css_files)
		self.toc_depth_var.set(int(data.get("toc-depth", 3)))
		metadata = data.get("metadata", {}) or {}
		self.title_var.set(metadata.get("title", ""))
		self.author_var.set(metadata.get("author", ""))

		# Resolve relative paths against the YAML's directory
		new_paths = []
		missing = []
		for rel in data["input-files"]:
			full = os.path.normpath(os.path.join(base_dir, rel))
			if os.path.exists(full):
				if full not in new_paths:
					new_paths.append(full)
			else:
				missing.append(rel)

		self.abs_paths = new_paths
		self.enabled_paths = set(new_paths)
		self.refresh_tree()

		if missing:
			messagebox.showwarning(
				"Missing files",
				f"{len(missing)} file(s) from the YAML could not be found and were skipped:\n\n"
				+ "\n".join(missing)
			)

	def _is_valid_input_file(self, path):
		name = os.path.basename(path)
		if name.startswith("~$"):
			return False
		if os.path.splitext(name)[1].lower() not in SUPPORTED_EXTENSIONS:
			return False
		return True

	def add_files(self):
		files = filedialog.askopenfilenames(
			filetypes=[
				("Supported files", "*.md *.docx *.dita"),
				("Markdown", "*.md"),
				("Word documents", "*.docx"),
				("DITA", "*.dita"),
				("All files", "*.*"),
			]
		)
		dupes = 0
		skipped = 0
		for file in files:
			full = os.path.abspath(file)
			if not self._is_valid_input_file(full):
				skipped += 1
				continue
			if full not in self.abs_paths:
				self.abs_paths.append(full)
				self.enabled_paths.add(full)
			else:
				dupes += 1
		self.refresh_tree()
		parts = []
		if dupes:
			parts.append(f"{dupes} duplicate(s) skipped")
		if skipped:
			parts.append(f"{skipped} temp file(s) skipped")
		if parts:
			self.status_var.set(", ".join(parts) + ".")

	def add_folder(self):
		folder = filedialog.askdirectory()
		if not folder:
			return

		dupes = 0
		skipped = 0
		for root, _, files in os.walk(folder):
			for file in files:
				full = os.path.abspath(os.path.join(root, file))
				if not self._is_valid_input_file(full):
					if os.path.basename(full).startswith("~$"):
						skipped += 1
					continue
				if full not in self.abs_paths:
					self.abs_paths.append(full)
					self.enabled_paths.add(full)
				else:
					dupes += 1

		self.refresh_tree()
		parts = []
		if dupes:
			parts.append(f"{dupes} duplicate(s) skipped")
		if skipped:
			parts.append(f"{skipped} temp file(s) skipped")
		if parts:
			self.status_var.set(", ".join(parts) + ".")

	def clear_all(self):
		if not self.abs_paths:
			return
		if messagebox.askyesno("Clear All", "Remove all files from the list?"):
			self.abs_paths.clear()
			self.enabled_paths.clear()
			self.refresh_tree()

	def remove_selected(self):
		selected = self.tree.selection()
		if not selected:
			return
		item = selected[0]
		path = self.tree.item(item)["tags"][0]
		self.abs_paths.remove(path)
		self.enabled_paths.discard(path)
		self.refresh_tree()

	def move_up(self):
		selected = self.tree.selection()
		if not selected:
			return
		item = selected[0]
		idx = self.tree.index(item)
		if idx == 0:
			return
		self.abs_paths.insert(idx - 1, self.abs_paths.pop(idx))
		self.refresh_tree()
		# Re-select the moved item
		children = self.tree.get_children()
		self.tree.selection_set(children[idx - 1])
		self.tree.see(children[idx - 1])

	def move_down(self):
		selected = self.tree.selection()
		if not selected:
			return
		item = selected[0]
		idx = self.tree.index(item)
		if idx >= len(self.abs_paths) - 1:
			return
		self.abs_paths.insert(idx + 1, self.abs_paths.pop(idx))
		self.refresh_tree()
		children = self.tree.get_children()
		self.tree.selection_set(children[idx + 1])
		self.tree.see(children[idx + 1])

	def _select_all(self):
		self.enabled_paths = set(self.abs_paths)
		self.refresh_tree()

	def _deselect_all(self):
		self.enabled_paths.clear()
		self.refresh_tree()

	def _toggle_enabled(self, item):
		path = self.tree.item(item)["tags"][0]
		if path in self.enabled_paths:
			self.enabled_paths.discard(path)
			self.tree.set(item, "enabled", "☐")
		else:
			self.enabled_paths.add(path)
			self.tree.set(item, "enabled", "☑")

	def refresh_tree(self):
		self.tree.delete(*self.tree.get_children())
		if not self.abs_paths:
			return
		try:
			base = os.path.commonpath(self.abs_paths)
			if os.path.isfile(base):
				base = os.path.dirname(base)
		except ValueError:
			base = ""
		for path in self.abs_paths:
			rel = os.path.relpath(path, base) if base else path
			folder = os.path.dirname(rel)
			check = "☑" if path in self.enabled_paths else "☐"
			title = get_file_title(path)
			self.tree.insert("", tk.END, values=(check, title, folder), tags=(path,))

	def browse_output(self):
		fmt = self.format_var.get()
		ext = FORMAT_EXTENSIONS.get(fmt, ".pdf")
		filetypes = FORMAT_FILETYPES.get(fmt, [("All files", "*.*")])
		path = filedialog.asksaveasfilename(
			defaultextension=ext,
			filetypes=filetypes + [("All files", "*.*")],
		)
		if path:
			self.output_var.set(path)

	def _log(self, text):
		self.log_text.configure(state="normal")
		self.log_text.insert(tk.END, text + "\n")
		self.log_text.see(tk.END)
		self.log_text.configure(state="disabled")

	def _log_clear(self):
		self.log_text.configure(state="normal")
		self.log_text.delete("1.0", tk.END)
		self.log_text.configure(state="disabled")

	def _update_timer(self):
		if getattr(self, "_pandoc_running", False):
			elapsed = int(time.time() - self._pandoc_start)
			self.status_var.set(f"Running pandoc… {elapsed}s")
			self.root.after(1000, self._update_timer)

	def run_pandoc(self):
		if not self.abs_paths:
			messagebox.showwarning("Run Pandoc", "No input files.")
			return
		output = self.output_var.get().strip()
		if not output:
			messagebox.showwarning("Run Pandoc", "No output file path set. Use the Browse button in Pandoc Options.")
			return

		active = [p for p in self.abs_paths if p in self.enabled_paths]
		if not active:
			messagebox.showwarning("Run Pandoc", "No files are enabled. Check at least one file.")
			return
		fmt = self.format_var.get()

		# Build the output-phase command (reads from JSON AST on stdin)
		out_cmd = ["-f", "json", "-o", output, "--to", fmt]
		if fmt == "pdf":
			out_cmd += [f"--pdf-engine={self.engine_var.get()}"]
			out_cmd += ["--pdf-engine-opt=-interaction=nonstopmode"]
			if self.new_page_var.get():
				out_cmd += [f"--lua-filter={LUA_FILTER_PATH}"]
		elif fmt in ("html", "latex"):
			out_cmd.append("--standalone")
			if fmt == "html" and self.sidebar_toc_var.get():
				out_dir = os.path.dirname(os.path.abspath(output))
				css_dest = os.path.join(out_dir, "toc-sidebar.css")
				if os.path.abspath(css_dest) != os.path.abspath(CSS_SIDEBAR_PATH):
					import shutil
					shutil.copy2(CSS_SIDEBAR_PATH, css_dest)
				out_cmd += ["--css", "toc-sidebar.css"]
		if self.toc_var.get():
			out_cmd.append("--toc")
			out_cmd.append(f"--toc-depth={self.toc_depth_var.get()}")
		if self.number_var.get():
			out_cmd.append("--number-sections")
		if self.title_var.get():
			out_cmd += ["-M", f"title={self.title_var.get()}"]
		if self.author_var.get():
			out_cmd += ["-M", f"author={self.author_var.get()}"]

		self._log_clear()
		self._log(f"$ pandoc [{len(active)} files] -o {os.path.basename(output)} --to {fmt} ...")
		self.run_btn.state(["disabled"])
		self.cancel_btn.pack(side=tk.LEFT)
		self._pandoc_running = True
		self._pandoc_start = time.time()
		self._pandoc_proc = None
		self._update_timer()

		def worker():
			try:
				# Phase 1: convert each file individually to pandoc JSON AST
				all_blocks = []
				api_version = None
				meta = {}
				for f in active:
					self.root.after(0, lambda n=os.path.basename(f): self._log(f"  reading {n}…"))
					result = subprocess.run(
						["pandoc", f, "-t", "json"],
						stdin=subprocess.DEVNULL,
						capture_output=True,
						text=True,
					)
					for line in result.stderr.splitlines():
						line = line.strip()
						if line:
							self.root.after(0, lambda l=line: self._log(l))
					if result.returncode != 0:
						self.root.after(0, lambda n=os.path.basename(f): self._pandoc_error(f"Failed to read {n}. See log."))
						return
					ast = json.loads(result.stdout.translate(_C1_MAP))
					if api_version is None:
						api_version = ast.get("pandoc-api-version")
						meta = ast.get("meta", {})
					all_blocks.extend(ast.get("blocks", []))

				# Phase 2: merge into one AST and convert to output format
				combined_json = json.dumps({
					"pandoc-api-version": api_version,
					"meta": meta,
					"blocks": all_blocks,
				})
				self.root.after(0, lambda: self._log(f"  building {os.path.basename(output)}…"))
				proc = subprocess.Popen(
					["pandoc"] + out_cmd,
					stdin=subprocess.PIPE,
					stdout=subprocess.DEVNULL,
					stderr=subprocess.PIPE,
					text=True, bufsize=1,
					start_new_session=True,
				)
				self._pandoc_proc = proc
				# Write stdin in a thread so large payloads don't deadlock
				def _write():
					proc.stdin.write(combined_json)
					proc.stdin.close()
				threading.Thread(target=_write, daemon=True).start()
				for line in iter(proc.stderr.readline, ""):
					line = line.rstrip()
					if line:
						self.root.after(0, lambda l=line: self._log(l))
				proc.wait()
				if proc.returncode == 0:
					self.root.after(0, self._pandoc_success)
				elif proc.returncode == -9:
					self.root.after(0, lambda: self._pandoc_error("Cancelled."))
				else:
					self.root.after(0, lambda: self._pandoc_error("Pandoc exited with an error. See log above."))
			except FileNotFoundError:
				self.root.after(0, lambda: self._pandoc_error("pandoc not found. Is it installed and on your PATH?"))

		threading.Thread(target=worker, daemon=True).start()

	def _cancel_pandoc(self):
		proc = getattr(self, "_pandoc_proc", None)
		if proc and proc.poll() is None:
			import os, signal
			try:
				os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
			except Exception:
				proc.kill()
		self.cancel_btn.pack_forget()

	def _pandoc_success(self):
		self._pandoc_running = False
		elapsed = int(time.time() - self._pandoc_start)
		self.run_btn.state(["!disabled"])
		self.cancel_btn.pack_forget()
		self.status_var.set(f"Done in {elapsed}s.")
		self._log(f"✓ Done in {elapsed}s → {self.output_var.get()}")
		messagebox.showinfo("Run Pandoc", f"Built successfully in {elapsed}s:\n{self.output_var.get()}")

	def _pandoc_error(self, msg):
		self._pandoc_running = False
		self.run_btn.state(["!disabled"])
		self.cancel_btn.pack_forget()
		self.status_var.set("Error — see log.")
		self._log(f"✗ {msg}")
		if msg != "Cancelled.":
			messagebox.showerror("Pandoc Error", msg)

	def save_yaml(self):
		if not self.abs_paths:
			messagebox.showwarning("No files", "No files to save.")
			return

		save_path = filedialog.asksaveasfilename(
			defaultextension=".yaml",
			filetypes=[("YAML files", "*.yaml *.yml")]
		)
		if not save_path:
			return

		base_dir = os.path.dirname(save_path)

		ordered_paths = []
		for item in self.tree.get_children():
			abs_path = self.tree.item(item)["tags"][0]
			if abs_path in self.enabled_paths:
				rel = os.path.relpath(abs_path, base_dir)
				ordered_paths.append(rel)

		fmt = self.format_var.get()
		data = {
			"input-files": ordered_paths,
			"to": fmt,
		}

		if fmt == "pdf":
			data["pdf-engine"] = self.engine_var.get()
			if self.new_page_var.get():
				filter_dest = os.path.join(base_dir, "newpage-h1.lua")
				if os.path.abspath(filter_dest) != os.path.abspath(LUA_FILTER_PATH):
					import shutil
					shutil.copy2(LUA_FILTER_PATH, filter_dest)
				data["filters"] = ["newpage-h1.lua"]
		elif fmt in ("html", "latex"):
			data["standalone"] = True
			if fmt == "html" and self.sidebar_toc_var.get():
				css_dest = os.path.join(base_dir, "toc-sidebar.css")
				if os.path.abspath(css_dest) != os.path.abspath(CSS_SIDEBAR_PATH):
					import shutil
					shutil.copy2(CSS_SIDEBAR_PATH, css_dest)
				data["css"] = ["toc-sidebar.css"]

		if self.toc_var.get():
			data["toc"] = True
			data["toc-depth"] = self.toc_depth_var.get()

		if self.number_var.get():
			data["number-sections"] = True

		metadata = {}
		if self.title_var.get():
			metadata["title"] = self.title_var.get()
		if self.author_var.get():
			metadata["author"] = self.author_var.get()

		with open(save_path, "w", encoding="utf-8") as f:
			top = {}
			if metadata:
				top["metadata"] = metadata
			for key in ("to", "pdf-engine", "filters", "standalone", "css", "toc", "toc-depth", "number-sections"):
				if key in data:
					top[key] = data[key]
			f.write("# ----- settings -----\n")
			f.write(yaml.safe_dump(top, sort_keys=False))
			f.write("# ----- settings -----\n\n")
			yaml.safe_dump({"input-files": ordered_paths}, f, sort_keys=False)

		messagebox.showinfo("Saved", "Pandoc defaults YAML saved successfully.")


if __name__ == "__main__":
	root = tk.Tk()
	app = MapMakerApp(root)
	root.mainloop()
