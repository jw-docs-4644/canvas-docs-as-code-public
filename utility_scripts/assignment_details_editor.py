import os
import sys
import csv
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from tkinter import ttk, messagebox
import frontmatter
from canvasapi import Canvas
from config_loader import load_canvas_config, load_course_id

API_URL, API_KEY = load_canvas_config()
COURSE_ID = load_course_id()

class AssignmentManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Assignment Manager (Live Totals)")
        
        self.content_folders = ["Assignments", "Discussions"]
        self.all_assignments_data = []
        self.module_order_map = {} 
        
        self.rubric_data_map = self.get_csv_rubric_data()
        self.rubric_display_list = ["None"] + [f"{t} ({p} pts)" for t, p in self.rubric_data_map.items()]
        
        try:
            self.status_label = tk.Label(self.root, text="Connecting to Canvas...", fg="blue")
            self.status_label.pack(pady=5)
            self.canvas = Canvas(API_URL, API_KEY)
            self.course = self.canvas.get_course(COURSE_ID)
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to Canvas: {e}")
            return

        self.setup_ui()
        self.load_assignments()

    def get_csv_rubric_data(self):
        totals = {}
        possible_paths = ["rubrics.csv", "Rubrics/rubrics.csv"]
        csv_path = next((p for p in possible_paths if os.path.exists(p)), None)
        if csv_path:
            with open(csv_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    title = row.get('rubric_title', '').strip()
                    pts_val = row.get('pts_1', 0)
                    if title:
                        try:
                            totals[title] = totals.get(title, 0) + float(pts_val)
                        except: pass
        for title in totals:
            if totals[title].is_integer(): totals[title] = int(totals[title])
        return totals

    def calculate_course_total(self, *args):
        """Sums up all values in the pts_var fields across the course."""
        total = 0.0
        for data in self.all_assignments_data:
            try:
                val = data['pts_var'].get().strip()
                if val:
                    total += float(val)
            except ValueError:
                pass
        
        display_total = int(total) if total.is_integer() else round(total, 2)
        self.total_points_var.set(f"COURSE TOTAL: {display_total} PTS")

    def on_rubric_change(self, data, *args):
        selected_display = data['rubric_var'].get()
        if selected_display == "None": return 
        raw_title = selected_display.split(" (")[0]
        if raw_title in self.rubric_data_map:
            new_total = self.rubric_data_map[raw_title]
            data['pts_var'].set(str(new_total))

    def setup_ui(self):
        # 1. SUMMARY BAR (Always at the very top)
        summary_frame = tk.Frame(self.root, bg="#2c3e50", pady=10)
        summary_frame.pack(fill="x")

        self.total_points_var = tk.StringVar(value="COURSE TOTAL: 0 PTS")
        total_label = tk.Label(summary_frame, textvariable=self.total_points_var, 
                               font=('Arial', 14, 'bold'), fg="#ecf0f1", bg="#2c3e50")
        total_label.pack()

        # 2. CONTROL BAR (Sorting)
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(control_frame, text="Sort By: ").pack(side="left")
        self.sort_var = tk.StringVar(value="Module Order")
        sort_menu = ttk.Combobox(control_frame, textvariable=self.sort_var, 
                                 values=["Module Order", "Alphabetical"], state="readonly")
        sort_menu.pack(side="left", padx=5)
        sort_menu.bind("<<ComboboxSelected>>", lambda e: self.redraw_rows())

        # 3. SCROLLABLE CONTENT
        self.container = ttk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        self.canvas_widget = tk.Canvas(self.container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas_widget.yview)
        self.scrollable_frame = ttk.Frame(self.canvas_widget)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas_widget.configure(scrollregion=self.canvas_widget.bbox("all")))
        self.canvas_frame_window = self.canvas_widget.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas_widget.bind('<Configure>', lambda e: self.canvas_widget.itemconfig(self.canvas_frame_window, width=e.width))
        self.canvas_widget.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas_widget.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Gestures
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Button-4>", self._on_mousewheel)
        self.root.bind_all("<Button-5>", self._on_mousewheel)

        self.save_btn = tk.Button(self.root, text="SYNC CHANGES ONLY", command=self.save_all, 
                                  bg="#27ae60", fg="white", font=('Arial', 10, 'bold'), pady=10)
        self.save_btn.pack(fill="x", padx=20, pady=10)

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0: self.canvas_widget.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0: self.canvas_widget.yview_scroll(1, "units")

    def convert_to_underscore_style(self, text):
        if not text: return ""
        return re.sub(r'_+', '_', re.sub(r'[^a-zA-Z0-9]', '_', text)).strip('_').lower()

    def update_local_file(self, name, pts, rubric, due, lock):
        target = self.convert_to_underscore_style(name)
        clean_r = rubric.split(" (")[0] if " (" in rubric else rubric
        for folder in self.content_folders:
            if not os.path.exists(folder): continue
            for filename in os.listdir(folder):
                if self.convert_to_underscore_style(filename.replace(".md", "")) == target:
                    file_path = os.path.join(folder, filename)
                    post = frontmatter.load(file_path)
                    if (str(post.get('points')) == str(pts) and str(post.get('rubric')) == str(clean_r) and 
                        str(post.get('due_at', "")) == str(due) and str(post.get('lock_at', "")) == str(lock)):
                        return False
                    post['points'] = pts
                    post['rubric'] = clean_r
                    post['due_at'] = due
                    post['lock_at'] = lock
                    with open(file_path, 'wb') as f:
                        frontmatter.dump(post, f)
                    return True
        return False

    def load_assignments(self):
        self.status_label.config(text="Mapping Canvas Module Order...", fg="blue")
        self.root.update()
        try:
            name_to_pos, name_to_module = {}, {}
            for m in self.course.get_modules():
                self.module_order_map[m.name] = m.position 
                for i, item in enumerate(m.get_module_items()):
                    name_to_pos[item.title] = item.position 
                    name_to_module[item.title] = m.name

            for a in self.course.get_assignments():
                p = a.points_possible
                p_str = str(int(p)) if p is not None and p.is_integer() else str(p) if p is not None else "0"
                curr_r = a.rubric_settings.get('title', 'None') if hasattr(a, 'rubric_settings') else "None"
                display_r = f"{curr_r} ({self.rubric_data_map.get(curr_r, 0)} pts)" if curr_r in self.rubric_data_map else "None"
                due_v = a.due_at[:10] if getattr(a, 'due_at', None) else ""
                lock_v = a.lock_at[:10] if getattr(a, 'lock_at', None) else ""
                
                mod_name = name_to_module.get(a.name, "Unassigned")
                
                pts_var = tk.StringVar(value=p_str)
                rubric_var = tk.StringVar(value=display_r)
                
                data_package = {
                    'obj': a, 'name': a.name, 'module_name': mod_name,
                    'module_index': self.module_order_map.get(mod_name, 999),
                    'item_index': name_to_pos.get(a.name, 999),
                    'pts_var': pts_var, 'rubric_var': rubric_var,
                    'due_var': tk.StringVar(value=due_v), 'lock_var': tk.StringVar(value=lock_v),
                    'snapshot': {'pts': p_str, 'rubric': display_r, 'due': due_v, 'lock': lock_v}
                }

                rubric_var.trace_add("write", lambda *args, d=data_package: self.on_rubric_change(d, *args))
                pts_var.trace_add("write", self.calculate_course_total)

                self.all_assignments_data.append(data_package)
            
            self.calculate_course_total() 
            self.redraw_rows()
            self.status_label.config(text="Ready.", fg="green")
        except Exception as e:
            print(f"Load Error: {e}")

    def redraw_rows(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        headers = ["Assignment Name", "Rubric Selection", "Pts", "Final Due\n(yyy-mm-dd)", "Lock Date\n(yyy-mm-dd)"]
        for i, h in enumerate(headers):
            ttk.Label(self.scrollable_frame, text=h, font=('Arial', 9, 'bold')).grid(row=0, column=i, padx=10, pady=5)

        sort_key = (lambda x: (x['module_index'], x['item_index'])) if self.sort_var.get() == "Module Order" else (lambda x: x['name'].lower())
        
        last_module, current_row = None, 1
        for data in sorted(self.all_assignments_data, key=sort_key):
            if self.sort_var.get() == "Module Order" and data['module_name'] != last_module:
                last_module = data['module_name']
                header_frame = tk.Frame(self.scrollable_frame, bg="#ecf0f1")
                header_frame.grid(row=current_row, column=0, columnspan=5, sticky="ew", pady=(10, 2))
                tk.Label(header_frame, text=f"📂 {last_module.upper()}", font=('Arial', 9, 'bold'), bg="#ecf0f1").pack(side="left", padx=5)
                current_row += 1

            ttk.Label(self.scrollable_frame, text=data['name'], width=40).grid(row=current_row, column=0, sticky="w", padx=10)
            ttk.Combobox(self.scrollable_frame, textvariable=data['rubric_var'], values=self.rubric_display_list, state="readonly", width=30).grid(row=current_row, column=1, padx=5)
            ttk.Entry(self.scrollable_frame, textvariable=data['pts_var'], width=8).grid(row=current_row, column=2, padx=5)
            ttk.Entry(self.scrollable_frame, textvariable=data['due_var'], width=15).grid(row=current_row, column=3, padx=5)
            ttk.Entry(self.scrollable_frame, textvariable=data['lock_var'], width=15).grid(row=current_row, column=4, padx=5)
            current_row += 1

    def save_all(self):
        print("\n🚀 SYNCING...")
        self.status_label.config(text="Syncing...", fg="blue")
        self.root.update()
        canvas_rubrics = {r.title: r.id for r in self.course.get_rubrics()}
        ISO_TIME = "T06:59:00Z"
        update_count = 0
        for data in self.all_assignments_data:
            c_pts, c_rub = data['pts_var'].get().strip(), data['rubric_var'].get()
            c_due, c_lock = data['due_var'].get().strip(), data['lock_var'].get().strip()
            snap = data['snapshot']
            if (c_pts == snap['pts'] and c_rub == snap['rubric'] and c_due == snap['due'] and c_lock == snap['lock']): continue
            try:
                update_count += 1
                p_val = float(c_pts) if c_pts else 0
                if p_val.is_integer(): p_val = int(p_val)
                self.update_local_file(data['name'], p_val, c_rub, c_due, c_lock)
                payload = {'points_possible': p_val}
                if len(c_due) == 10: payload['due_at'] = f"{c_due}{ISO_TIME}"
                if len(c_lock) == 10: payload['lock_at'] = f"{c_lock}{ISO_TIME}"
                data['obj'].edit(assignment=payload)
                if c_rub != snap['rubric']:
                    raw_title = c_rub.split(" (")[0] if " (" in c_rub else c_rub
                    if raw_title in canvas_rubrics:
                        self.course.create_rubric_association(rubric_association={'rubric_id': canvas_rubrics[raw_title], 'association_id': data['obj'].id, 'association_type': 'Assignment', 'use_for_grading': True, 'purpose': 'grading'})
                        data['obj'].edit(assignment={'points_possible': p_val})
                data['snapshot'].update({'pts': str(p_val), 'rubric': c_rub, 'due': c_due, 'lock': c_lock})
            except Exception as e: print(f"❌ Error: {e}")
        messagebox.showinfo("Success", f"Updated {update_count} items.")
        self.status_label.config(text="Ready.", fg="green")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1200x850")
    app = AssignmentManagerGUI(root)
    root.mainloop()
