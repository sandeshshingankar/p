import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import requests

# ---------------- College App - Professional UI ----------------
# CRUD-enabled version:
# Assignments, Exams, Results, Notices and Timetable
# use the Flask backend API for Add / Edit / Delete / Refresh.

root = tk.Tk()
root.title("College App - Professional UI")
root.geometry("1250x750")
root.minsize(1050, 650)
root.configure(bg="#f4f6fb")

# Colors
SIDEBAR = "#1f2937"
PRIMARY = "#2563eb"
WHITE = "#ffffff"
TEXT = "#111827"
MUTED = "#6b7280"
CARD = "#ffffff"
DANGER = "#ef4444"
SUCCESS = "#16a34a"
API_BASE = "http://127.0.0.1:5000/v1"


def clear_content():
    for widget in content.winfo_children():
        widget.destroy()


def title_lbl(text, subtitle=""):
    tk.Label(
        content, text=text, font=("Arial", 24, "bold"),
        bg="#f4f6fb", fg=TEXT
    ).pack(anchor="w", padx=25, pady=(20, 2))
    if subtitle:
        tk.Label(
            content, text=subtitle, font=("Arial", 11),
            bg="#f4f6fb", fg=MUTED
        ).pack(anchor="w", padx=25, pady=(0, 15))


def card(parent, heading, value):
    frame = tk.Frame(
        parent, bg=CARD,
        highlightbackground="#e5e7eb", highlightthickness=1
    )
    frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)
    tk.Label(
        frame, text=heading, font=("Arial", 11),
        bg=CARD, fg=MUTED
    ).pack(anchor="w", padx=18, pady=(15, 2))
    lbl_val = tk.Label(
        frame, text=value, font=("Arial", 22, "bold"),
        bg=CARD, fg=PRIMARY
    )
    lbl_val.pack(anchor="w", padx=18, pady=(0, 15))
    return lbl_val


def api_get(endpoint):
    try:
        res = requests.get(f"{API_BASE}{endpoint}", timeout=4)
        if res.status_code == 200:
            return res.json()
        return None
    except requests.exceptions.RequestException:
        return "OFFLINE"


def api_request(method, endpoint, payload=None):
    try:
        res = requests.request(
            method,
            f"{API_BASE}{endpoint}",
            json=payload,
            timeout=5
        )
        try:
            data = res.json()
        except ValueError:
            data = {}
        return res.status_code, data
    except requests.exceptions.RequestException:
        return None, {"error": "Backend server is offline."}


def extract_list(data, keys=("items", "data", "results")):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in keys:
            if isinstance(data.get(key), list):
                return data[key]
    return []


def get_id(row):
    return row.get("id", row.get("_id", row.get("ID", "")))


def show_backend_error(status, data, action="Operation"):
    if status is None:
        messagebox.showerror(
            "Backend Offline",
            "Backend server is OFF.\nStart your Flask main.py first."
        )
        return
    if status not in (200, 201):
        error = data.get("error", data.get("message", "Unknown backend error"))
        messagebox.showerror("Error", f"{action} failed.\n\n{error}")


def make_action_buttons(parent, add_command, edit_command, delete_command):
    bar = tk.Frame(parent, bg="#f4f6fb")
    bar.pack(fill="x", padx=25, pady=(0, 8))

    tk.Button(
        bar, text="+ Add", command=add_command,
        bg=PRIMARY, fg=WHITE, relief="flat",
        font=("Arial", 10, "bold"), padx=18, pady=7
    ).pack(side="left", padx=(0, 6))

    tk.Button(
        bar, text="Edit", command=edit_command,
        bg=WHITE, fg=TEXT, relief="solid", bd=1,
        font=("Arial", 10), padx=18, pady=7
    ).pack(side="left", padx=6)

    tk.Button(
        bar, text="Delete", command=delete_command,
        bg=DANGER, fg=WHITE, relief="flat",
        font=("Arial", 10, "bold"), padx=18, pady=7
    ).pack(side="left", padx=6)

    return bar


def open_form(title, fields, initial=None, on_save=None):
    """
    Generic Add/Edit form.
    fields = [(key, label, type, values)]
    type: entry, date, combo, text
    """
    initial = initial or {}

    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("620x620")
    win.minsize(560, 500)
    win.configure(bg="#f4f6fb")
    win.transient(root)
    win.grab_set()

    outer = tk.Frame(win, bg=CARD, highlightbackground="#e5e7eb",
                     highlightthickness=1)
    outer.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(
        outer, text=title, font=("Arial", 18, "bold"),
        bg=CARD, fg=TEXT
    ).pack(anchor="w", padx=22, pady=(20, 15))

    form = tk.Frame(outer, bg=CARD)
    form.pack(fill="both", expand=True, padx=22)

    widgets = {}

    for row_no, spec in enumerate(fields):
        key, label, kind, values = (
            spec[0], spec[1], spec[2], spec[3] if len(spec) > 3 else None
        )

        tk.Label(
            form, text=label, font=("Arial", 10, "bold"),
            bg=CARD, fg=TEXT
        ).grid(row=row_no, column=0, padx=(0, 18), pady=7, sticky="nw")

        value = initial.get(key, "")

        if kind == "text":
            widget = tk.Text(form, width=35, height=4, font=("Arial", 10))
            widget.insert("1.0", str(value))
        elif kind == "date":
            widget = DateEntry(
                form, width=32, date_pattern="yyyy-mm-dd",
                background=PRIMARY, foreground="white"
            )
            if value:
                try:
                    widget.set_date(value)
                except Exception:
                    pass
        elif kind == "combo":
            widget = ttk.Combobox(
                form, values=values or [], width=33,
                font=("Arial", 10), state="readonly"
            )
            if value in (values or []):
                widget.set(value)
        else:
            widget = tk.Entry(
                form, width=35, font=("Arial", 10),
                bg="#f9fafb", relief="solid"
            )
            widget.insert(0, str(value))

        widget.grid(row=row_no, column=1, padx=5, pady=7, sticky="ew")
        widgets[key] = widget

    form.columnconfigure(1, weight=1)

    def collect():
        payload = {}
        for key, widget in widgets.items():
            if isinstance(widget, tk.Text):
                payload[key] = widget.get("1.0", "end").strip()
            else:
                payload[key] = widget.get().strip()

        if on_save:
            if on_save(payload):
                win.destroy()

    tk.Button(
        outer, text="Save", command=collect,
        bg=PRIMARY, fg=WHITE, relief="flat",
        font=("Arial", 11, "bold"), padx=30, pady=9
    ).pack(side="left", padx=(22, 8), pady=20)

    tk.Button(
        outer, text="Cancel", command=win.destroy,
        bg=WHITE, fg=TEXT, relief="solid", bd=1,
        font=("Arial", 11), padx=25, pady=9
    ).pack(side="left", pady=20)


# ---------------- Dashboard ----------------

def dashboard():
    clear_content()
    title_lbl(
        "College Dashboard",
        "Overview of college activities and student statistics"
    )

    stats = tk.Frame(content, bg="#f4f6fb")
    stats.pack(fill="x", padx=15)

    data_all = api_get("/students/all")
    total_stu = str(len(data_all)) if isinstance(data_all, list) else (
        "Offline" if data_all == "OFFLINE" else "0"
    )

    att_data = api_get("/attendance")
    att_val = (
        f"{att_data.get('overall', '--')}%"
        if isinstance(att_data, dict)
        else ("Offline" if att_data == "OFFLINE" else "--%")
    )

    assignments_data = extract_list(api_get("/assignments"))
    notices_data = extract_list(api_get("/notices"))

    card(stats, "Total Students", total_stu)
    card(stats, "Attendance", att_val)
    card(stats, "Assignments", str(len(assignments_data)))
    card(stats, "Notices", str(len(notices_data)))

    mid_frame = tk.Frame(content, bg="#f4f6fb")
    mid_frame.pack(fill="both", expand=True, padx=25, pady=10)

    col1 = tk.Frame(mid_frame, bg="#f4f6fb")
    col1.pack(side="left", fill="both", expand=True, padx=(0, 10))

    col2 = tk.Frame(mid_frame, bg="#f4f6fb")
    col2.pack(side="right", fill="both", expand=True, padx=(10, 0))

    def section(parent, title, items):
        frm = tk.Frame(
            parent, bg=CARD,
            highlightbackground="#e5e7eb", highlightthickness=1
        )
        frm.pack(fill="both", expand=True, pady=8)
        tk.Label(
            frm, text=title, font=("Arial", 13, "bold"),
            bg=CARD, fg=TEXT
        ).pack(anchor="w", padx=15, pady=(15, 5))
        for item in items:
            tk.Label(
                frm, text=f"• {item}", font=("Arial", 11),
                bg=CARD, fg=MUTED, anchor="w"
            ).pack(anchor="w", padx=15, pady=3)

    exams = extract_list(api_get("/exams"))
    assignments = extract_list(api_get("/assignments"))
    notices = extract_list(api_get("/notices"))

    exam_items = []
    for e in exams[:3]:
        exam_items.append(
            f"{e.get('subject', 'Subject')} - {e.get('date', '')}"
        )
    if not exam_items:
        exam_items = ["No upcoming exams"]

    notice_items = []
    for n in notices[-3:]:
        notice_items.append(n.get("title", "Notice"))
    if not notice_items:
        notice_items = ["No notices"]

    assignment_items = []
    for a in assignments[:3]:
        assignment_items.append(
            f"{a.get('subject', 'Subject')}: "
            f"{a.get('title', 'Assignment')} - Due {a.get('due_date', '')}"
        )
    if not assignment_items:
        assignment_items = ["No assignments"]

    section(col1, "Upcoming Exams", exam_items)
    section(col1, "Recent Notices", notice_items)
    section(col2, "Recent Assignments", assignment_items)
    section(col2, "Attendance Overview", [
        f"Overall: {att_val}",
        "Use Attendance module for subject-wise details."
    ])

    ai = tk.Frame(content, bg=PRIMARY)
    ai.pack(fill="x", padx=25, pady=10)
    tk.Label(
        ai, text="AI Study Assistant", font=("Arial", 15, "bold"),
        bg=PRIMARY, fg=WHITE
    ).pack(anchor="w", padx=18, pady=(10, 2))
    tk.Label(
        ai,
        text="Get instant answers, generate study plans, and predict grades.",
        font=("Arial", 10), bg=PRIMARY, fg=WHITE
    ).pack(anchor="w", padx=18, pady=(0, 8))


# ---------------- Students Database ----------------

def profile():
    clear_content()
    title_lbl("Students Database", "View, Edit, or Delete registered students")

    frame = tk.Frame(
        content, bg=CARD,
        highlightbackground="#e5e7eb", highlightthickness=1
    )
    frame.pack(fill="both", expand=True, padx=25, pady=10)

    scroll_y = ttk.Scrollbar(frame, orient="vertical")
    scroll_y.pack(side="right", fill="y")
    scroll_x = ttk.Scrollbar(frame, orient="horizontal")
    scroll_x.pack(side="bottom", fill="x")

    cols = ("ID", "Name", "Course", "Year", "Div", "Email", "Phone", "Att.")
    tree = ttk.Treeview(
        frame, columns=cols, show="headings",
        yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set
    )

    widths = [50, 150, 80, 80, 50, 190, 110, 60]
    for i, col in enumerate(cols):
        tree.heading(col, text=col)
        tree.column(col, width=widths[i], anchor="center")

    scroll_y.config(command=tree.yview)
    scroll_x.config(command=tree.xview)
    tree.pack(fill="both", expand=True)

    data = api_get("/students/all")
    if data == "OFFLINE":
        tree.insert(
            "", "end",
            values=("", "", "BACKEND OFFLINE", "Please start",
                    "Flask server", "", "", "")
        )
    elif data:
        for s in data:
            full_name = f"{s.get('first_name','')} {s.get('last_name','')}"
            tree.insert(
                "", "end",
                values=(
                    s.get("id", ""), full_name, s.get("course", ""),
                    s.get("year", "1st Year"), s.get("division", "A"),
                    s.get("email", ""), s.get("mobile", ""), "85%"
                )
            )

    btn_frame = tk.Frame(content, bg="#f4f6fb")
    btn_frame.pack(fill="x", padx=25, pady=5)

    def delete_student():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning(
                "Warning", "Please select a student from the table first!"
            )
            return
        student_id = tree.item(selected, "values")[0]
        if not student_id:
            return
        if messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete Student ID: {student_id}?"
        ):
            status, data = api_request("DELETE", f"/student/{student_id}")
            if status == 200:
                messagebox.showinfo("Success", "Student deleted successfully!")
                profile()
            else:
                show_backend_error(status, data, "Delete")

    def edit_student():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a student first.")
            return
        values = tree.item(selected, "values")
        if not values or not values[0]:
            return

        student_id = values[0]
        initial = {
            "first_name": values[1].split(" ", 1)[0],
            "last_name": values[1].split(" ", 1)[1] if " " in values[1] else "",
            "course": values[2],
            "year": values[3],
            "division": values[4],
            "email": values[5],
            "mobile": values[6],
        }

        fields = [
            ("first_name", "First Name", "entry"),
            ("last_name", "Last Name", "entry"),
            ("email", "Email", "entry"),
            ("mobile", "Mobile", "entry"),
            ("course", "Course", "combo", ["BCA", "MCA", "BBA", "B.Tech"]),
            ("year", "Year", "combo", ["1st Year", "2nd Year", "3rd Year", "4th Year"]),
            ("division", "Division", "combo", ["A", "B", "C", "D"]),
        ]

        def save(payload):
            status, data = api_request(
                "PUT", f"/student/{student_id}", payload
            )
            if status in (200, 201):
                messagebox.showinfo("Success", "Student updated successfully!")
                profile()
                return True
            show_backend_error(status, data, "Update")
            return False

        open_form("Edit Student", fields, initial, save)

    tk.Button(
        btn_frame, text="Edit Student", command=edit_student,
        bg=WHITE, fg=TEXT, relief="solid", bd=1
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame, text="Delete Student", command=delete_student,
        bg=DANGER, fg=WHITE, relief="flat"
    ).pack(side="left", padx=5)


# ---------------- Register Student ----------------

def register_page():
    clear_content()
    title_lbl("Register Student", "Fill out the admission form")

    form = tk.Frame(
        content, bg=CARD,
        highlightbackground="#e5e7eb", highlightthickness=1
    )
    form.pack(fill="both", expand=True, padx=25, pady=10)

    def validate_mobile(P):
        return len(P) <= 10 if P.isdigit() or P == "" else False

    vcmd_mobile = (root.register(validate_mobile), "%P")

    tk.Label(form, text="Full Name*", bg=CARD,
             font=("Arial", 10, "bold")).grid(
        row=0, column=0, padx=20, pady=8, sticky="w"
    )
    ent_name = tk.Entry(form, width=30, font=("Arial", 11),
                        bg="#f9fafb", relief="solid")
    ent_name.grid(row=0, column=1, padx=20, pady=8)

    tk.Label(form, text="Email*", bg=CARD,
             font=("Arial", 10, "bold")).grid(
        row=1, column=0, padx=20, pady=8, sticky="w"
    )
    ent_email = tk.Entry(form, width=30, font=("Arial", 11),
                         bg="#f9fafb", relief="solid")
    ent_email.grid(row=1, column=1, padx=20, pady=8)

    tk.Label(form, text="Mobile*", bg=CARD,
             font=("Arial", 10, "bold")).grid(
        row=2, column=0, padx=20, pady=8, sticky="w"
    )
    ent_mobile = tk.Entry(
        form, width=30, font=("Arial", 11), bg="#f9fafb",
        relief="solid", validate="key", validatecommand=vcmd_mobile
    )
    ent_mobile.grid(row=2, column=1, padx=20, pady=8)

    tk.Label(form, text="Date of Birth*", bg=CARD,
             font=("Arial", 10, "bold")).grid(
        row=3, column=0, padx=20, pady=8, sticky="w"
    )
    ent_dob = DateEntry(
        form, width=28, background=PRIMARY,
        foreground="white", date_pattern="yyyy-mm-dd"
    )
    ent_dob.grid(row=3, column=1, padx=20, pady=8)

    tk.Label(form, text="Address*", bg=CARD,
             font=("Arial", 10, "bold")).grid(
        row=4, column=0, padx=20, pady=8, sticky="w"
    )
    ent_address = tk.Entry(
        form, width=30, font=("Arial", 11),
        bg="#f9fafb", relief="solid"
    )
    ent_address.grid(row=4, column=1, padx=20, pady=8)

    tk.Label(form, text="Course*", bg=CARD,
             font=("Arial", 10, "bold")).grid(
        row=0, column=2, padx=20, pady=8, sticky="w"
    )
    ent_course = ttk.Combobox(
        form, values=["BCA", "MCA", "BBA", "B.Tech"],
        font=("Arial", 11), width=28, state="readonly"
    )
    ent_course.grid(row=0, column=3, padx=20, pady=8)

    tk.Label(form, text="Year*", bg=CARD,
             font=("Arial", 10, "bold")).grid(
        row=1, column=2, padx=20, pady=8, sticky="w"
    )
    ent_year = ttk.Combobox(
        form, values=["1st Year", "2nd Year", "3rd Year", "4th Year"],
        font=("Arial", 11), width=28, state="readonly"
    )
    ent_year.grid(row=1, column=3, padx=20, pady=8)

    tk.Label(form, text="Division*", bg=CARD,
             font=("Arial", 10, "bold")).grid(
        row=2, column=2, padx=20, pady=8, sticky="w"
    )
    ent_div = ttk.Combobox(
        form, values=["A", "B", "C", "D"],
        font=("Arial", 11), width=28, state="readonly"
    )
    ent_div.grid(row=2, column=3, padx=20, pady=8)

    def submit_data():
        name_parts = ent_name.get().strip().split(" ", 1)
        f_name = name_parts[0] if name_parts else ""
        l_name = name_parts[1] if len(name_parts) > 1 else ""

        req_data = {
            "first_name": f_name,
            "last_name": l_name,
            "email": ent_email.get().strip(),
            "mobile": ent_mobile.get().strip(),
            "dob": ent_dob.get(),
            "gender": "Not Specified",
            "course": ent_course.get(),
            "year": ent_year.get(),
            "division": ent_div.get(),
            "address": ent_address.get().strip()
        }

        if not all([
            f_name, req_data["email"], req_data["mobile"],
            req_data["course"], req_data["year"], req_data["division"]
        ]):
            messagebox.showerror("Error", "All fields are mandatory!")
            return

        status, data = api_request("POST", "/register", req_data)
        if status in (200, 201):
            messagebox.showinfo(
                "Success", "Student Registered Successfully!"
            )
            ent_name.delete(0, "end")
            ent_email.delete(0, "end")
            ent_mobile.delete(0, "end")
            ent_address.delete(0, "end")
        else:
            show_backend_error(status, data, "Registration")

    tk.Button(
        form, text="Submit Registration", command=submit_data,
        bg=PRIMARY, fg=WHITE, font=("Arial", 11, "bold"),
        padx=30, pady=8, relief="flat"
    ).grid(row=5, column=1, columnspan=2, pady=25)


# ---------------- Generic CRUD Pages ----------------

def assignments():
    clear_content()
    title_lbl(
        "Assignments",
        "Add, edit and delete college assignments"
    )

    frame = tk.Frame(
        content, bg=CARD,
        highlightbackground="#e5e7eb", highlightthickness=1
    )
    frame.pack(fill="both", expand=True, padx=25, pady=10)

    cols = ("ID", "Subject", "Title", "Description", "Due Date", "Status")
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    widths = [45, 110, 190, 250, 100, 90]
    for i, col in enumerate(cols):
        tree.heading(col, text=col)
        tree.column(col, width=widths[i], anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load():
        for item in tree.get_children():
            tree.delete(item)
        data = extract_list(api_get("/assignments"))
        for a in data:
            tree.insert("", "end", values=(
                get_id(a),
                a.get("subject", ""),
                a.get("title", ""),
                a.get("description", ""),
                a.get("due_date", ""),
                a.get("status", "Pending")
            ))

    fields = [
        ("subject", "Subject", "combo",
         ["Python", "Java", "DBMS", "DCN", "Data Structures"]),
        ("title", "Assignment Title", "entry"),
        ("description", "Description", "text"),
        ("due_date", "Due Date", "date"),
        ("status", "Status", "combo", ["Pending", "Submitted", "Completed"]),
    ]

    def add():
        def save(payload):
            status, data = api_request("POST", "/assignments", payload)
            if status in (200, 201):
                messagebox.showinfo("Success", "Assignment added successfully!")
                load()
                return True
            show_backend_error(status, data, "Add Assignment")
            return False
        open_form("Add Assignment", fields, on_save=save)

    def edit():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select an assignment first.")
            return
        values = tree.item(selected, "values")
        item_id = values[0]
        initial = dict(zip(
            ["id", "subject", "title", "description", "due_date", "status"],
            values
        ))
        initial.pop("id", None)

        def save(payload):
            status, data = api_request(
                "PUT", f"/assignments/{item_id}", payload
            )
            if status in (200, 201):
                messagebox.showinfo("Success", "Assignment updated successfully!")
                load()
                return True
            show_backend_error(status, data, "Update Assignment")
            return False
        open_form("Edit Assignment", fields, initial, save)

    def delete():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select an assignment first.")
            return
        item_id = tree.item(selected, "values")[0]
        if messagebox.askyesno("Confirm Delete", "Delete this assignment?"):
            status, data = api_request(
                "DELETE", f"/assignments/{item_id}"
            )
            if status == 200:
                messagebox.showinfo("Success", "Assignment deleted successfully!")
                load()
            else:
                show_backend_error(status, data, "Delete Assignment")

    make_action_buttons(content, add, edit, delete)
    load()


def exams_results():
    clear_content()
    title_lbl(
        "Exams & Results",
        "Manage exam schedules and student results"
    )

    # Exams section
    tk.Label(
        content, text="Exam Schedule",
        font=("Arial", 16, "bold"), bg="#f4f6fb", fg=TEXT
    ).pack(anchor="w", padx=25, pady=(0, 5))

    exam_frame = tk.Frame(
        content, bg=CARD,
        highlightbackground="#e5e7eb", highlightthickness=1
    )
    exam_frame.pack(fill="x", padx=25, pady=(0, 5))

    exam_cols = (
        "ID", "Subject", "Exam Type", "Date",
        "Time", "Total Marks", "Passing Marks"
    )
    exam_tree = ttk.Treeview(
        exam_frame, columns=exam_cols,
        show="headings", height=6
    )
    exam_widths = [40, 140, 100, 100, 100, 100, 110]
    for i, col in enumerate(exam_cols):
        exam_tree.heading(col, text=col)
        exam_tree.column(col, width=exam_widths[i], anchor="center")
    exam_tree.pack(fill="x", padx=10, pady=10)

    exam_fields = [
        ("subject", "Subject", "entry"),
        ("exam_type", "Exam Type", "combo",
         ["Internal", "Mid-Term", "Practical", "Semester", "Unit Test"]),
        ("date", "Date", "date"),
        ("time", "Time", "entry"),
        ("total_marks", "Total Marks", "entry"),
        ("passing_marks", "Passing Marks", "entry"),
    ]

    def load_exams():
        for item in exam_tree.get_children():
            exam_tree.delete(item)
        for e in extract_list(api_get("/exams")):
            exam_tree.insert("", "end", values=(
                get_id(e), e.get("subject", ""), e.get("exam_type", ""),
                e.get("date", ""), e.get("time", ""),
                e.get("total_marks", ""), e.get("passing_marks", "")
            ))

    def add_exam():
        def save(payload):
            status, data = api_request("POST", "/exams", payload)
            if status in (200, 201):
                messagebox.showinfo("Success", "Exam added successfully!")
                load_exams()
                return True
            show_backend_error(status, data, "Add Exam")
            return False
        open_form("Add Exam", exam_fields, on_save=save)

    def edit_exam():
        selected = exam_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select an exam first.")
            return
        values = exam_tree.item(selected, "values")
        item_id = values[0]
        initial = dict(zip(
            ["id", "subject", "exam_type", "date", "time",
             "total_marks", "passing_marks"],
            values
        ))
        initial.pop("id", None)

        def save(payload):
            status, data = api_request(
                "PUT", f"/exams/{item_id}", payload
            )
            if status in (200, 201):
                messagebox.showinfo("Success", "Exam updated successfully!")
                load_exams()
                return True
            show_backend_error(status, data, "Update Exam")
            return False
        open_form("Edit Exam", exam_fields, initial, save)

    def delete_exam():
        selected = exam_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select an exam first.")
            return
        item_id = exam_tree.item(selected, "values")[0]
        if messagebox.askyesno("Confirm Delete", "Delete this exam?"):
            status, data = api_request(
                "DELETE", f"/exams/{item_id}"
            )
            if status == 200:
                messagebox.showinfo("Success", "Exam deleted successfully!")
                load_exams()
            else:
                show_backend_error(status, data, "Delete Exam")

    make_action_buttons(
        content, add_exam, edit_exam, delete_exam
    )
    load_exams()

    # Results section
    tk.Label(
        content, text="Student Results",
        font=("Arial", 16, "bold"), bg="#f4f6fb", fg=TEXT
    ).pack(anchor="w", padx=25, pady=(12, 5))

    result_frame = tk.Frame(
        content, bg=CARD,
        highlightbackground="#e5e7eb", highlightthickness=1
    )
    result_frame.pack(fill="both", expand=True, padx=25, pady=(0, 5))

    result_cols = (
        "ID", "Student ID", "Student", "Subject",
        "Marks", "Total", "Grade", "Result"
    )
    result_tree = ttk.Treeview(
        result_frame, columns=result_cols, show="headings"
    )
    result_widths = [40, 90, 150, 130, 70, 70, 70, 80]
    for i, col in enumerate(result_cols):
        result_tree.heading(col, text=col)
        result_tree.column(col, width=result_widths[i], anchor="center")
    result_tree.pack(fill="both", expand=True, padx=10, pady=10)

    result_fields = [
        ("student_id", "Student ID", "entry"),
        ("student_name", "Student Name", "entry"),
        ("subject", "Subject", "entry"),
        ("marks", "Marks", "entry"),
        ("total", "Total Marks", "entry"),
        ("grade", "Grade", "entry"),
        ("result", "Result", "combo", ["Pass", "Fail"]),
    ]

    def load_results():
        for item in result_tree.get_children():
            result_tree.delete(item)
        for r in extract_list(api_get("/results")):
            result_tree.insert("", "end", values=(
                get_id(r), r.get("student_id", ""),
                r.get("student_name", ""), r.get("subject", ""),
                r.get("marks", ""), r.get("total", ""),
                r.get("grade", ""), r.get("result", "")
            ))

    def add_result():
        def save(payload):
            status, data = api_request("POST", "/results", payload)
            if status in (200, 201):
                messagebox.showinfo("Success", "Result added successfully!")
                load_results()
                return True
            show_backend_error(status, data, "Add Result")
            return False
        open_form("Add Result", result_fields, on_save=save)

    def edit_result():
        selected = result_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a result first.")
            return
        values = result_tree.item(selected, "values")
        item_id = values[0]
        initial = dict(zip(
            ["id", "student_id", "student_name", "subject",
             "marks", "total", "grade", "result"],
            values
        ))
        initial.pop("id", None)

        def save(payload):
            status, data = api_request(
                "PUT", f"/results/{item_id}", payload
            )
            if status in (200, 201):
                messagebox.showinfo("Success", "Result updated successfully!")
                load_results()
                return True
            show_backend_error(status, data, "Update Result")
            return False
        open_form("Edit Result", result_fields, initial, save)

    def delete_result():
        selected = result_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a result first.")
            return
        item_id = result_tree.item(selected, "values")[0]
        if messagebox.askyesno("Confirm Delete", "Delete this result?"):
            status, data = api_request(
                "DELETE", f"/results/{item_id}"
            )
            if status == 200:
                messagebox.showinfo("Success", "Result deleted successfully!")
                load_results()
            else:
                show_backend_error(status, data, "Delete Result")

    make_action_buttons(
        content, add_result, edit_result, delete_result
    )
    load_results()


def notices():
    clear_content()
    title_lbl(
        "College Notices",
        "Add, edit and delete latest announcements"
    )

    frame = tk.Frame(
        content, bg=CARD,
        highlightbackground="#e5e7eb", highlightthickness=1
    )
    frame.pack(fill="both", expand=True, padx=25, pady=10)

    cols = ("ID", "Title", "Details", "Date", "Category")
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    widths = [45, 220, 330, 110, 110]
    for i, col in enumerate(cols):
        tree.heading(col, text=col)
        tree.column(col, width=widths[i], anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    fields = [
        ("title", "Notice Title", "entry"),
        ("details", "Notice Details", "text"),
        ("date", "Date", "date"),
        ("category", "Category", "combo",
         ["General", "Exam", "Holiday", "Academic", "Event"]),
    ]

    def load():
        for item in tree.get_children():
            tree.delete(item)
        for n in extract_list(api_get("/notices")):
            tree.insert("", "end", values=(
                get_id(n),
                n.get("title", ""),
                n.get("details", ""),
                n.get("date", ""),
                n.get("category", "General")
            ))

    def add():
        def save(payload):
            status, data = api_request("POST", "/notices", payload)
            if status in (200, 201):
                messagebox.showinfo("Success", "Notice added successfully!")
                load()
                return True
            show_backend_error(status, data, "Add Notice")
            return False
        open_form("Add Notice", fields, on_save=save)

    def edit():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a notice first.")
            return
        values = tree.item(selected, "values")
        item_id = values[0]
        initial = dict(zip(
            ["id", "title", "details", "date", "category"], values
        ))
        initial.pop("id", None)

        def save(payload):
            status, data = api_request(
                "PUT", f"/notices/{item_id}", payload
            )
            if status in (200, 201):
                messagebox.showinfo("Success", "Notice updated successfully!")
                load()
                return True
            show_backend_error(status, data, "Update Notice")
            return False
        open_form("Edit Notice", fields, initial, save)

    def delete():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a notice first.")
            return
        item_id = tree.item(selected, "values")[0]
        if messagebox.askyesno("Confirm Delete", "Delete this notice?"):
            status, data = api_request(
                "DELETE", f"/notices/{item_id}"
            )
            if status == 200:
                messagebox.showinfo("Success", "Notice deleted successfully!")
                load()
            else:
                show_backend_error(status, data, "Delete Notice")

    make_action_buttons(content, add, edit, delete)
    load()


def timetable():
    clear_content()
    title_lbl(
        "Class Timetable",
        "Manage weekly schedule for the current semester"
    )

    frame = tk.Frame(
        content, bg=CARD,
        highlightbackground="#e5e7eb", highlightthickness=1
    )
    frame.pack(fill="both", expand=True, padx=25, pady=10)

    cols = ("ID", "Time", "Monday", "Tuesday",
            "Wednesday", "Thursday", "Friday")
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    widths = [45, 110, 130, 130, 130, 130, 130]
    for i, col in enumerate(cols):
        tree.heading(col, text=col)
        tree.column(col, width=widths[i], anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    fields = [
        ("time", "Time", "entry"),
        ("monday", "Monday", "entry"),
        ("tuesday", "Tuesday", "entry"),
        ("wednesday", "Wednesday", "entry"),
        ("thursday", "Thursday", "entry"),
        ("friday", "Friday", "entry"),
    ]

    def load():
        for item in tree.get_children():
            tree.delete(item)
        for t in extract_list(api_get("/timetable")):
            tree.insert("", "end", values=(
                get_id(t), t.get("time", ""),
                t.get("monday", ""), t.get("tuesday", ""),
                t.get("wednesday", ""), t.get("thursday", ""),
                t.get("friday", "")
            ))

    def add():
        def save(payload):
            status, data = api_request("POST", "/timetable", payload)
            if status in (200, 201):
                messagebox.showinfo("Success", "Timetable added successfully!")
                load()
                return True
            show_backend_error(status, data, "Add Timetable")
            return False
        open_form("Add Timetable", fields, on_save=save)

    def edit():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a timetable row first.")
            return
        values = tree.item(selected, "values")
        item_id = values[0]
        initial = dict(zip(
            ["id", "time", "monday", "tuesday", "wednesday",
             "thursday", "friday"],
            values
        ))
        initial.pop("id", None)

        def save(payload):
            status, data = api_request(
                "PUT", f"/timetable/{item_id}", payload
            )
            if status in (200, 201):
                messagebox.showinfo("Success", "Timetable updated successfully!")
                load()
                return True
            show_backend_error(status, data, "Update Timetable")
            return False
        open_form("Edit Timetable", fields, initial, save)

    def delete():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a timetable row first.")
            return
        item_id = tree.item(selected, "values")[0]
        if messagebox.askyesno("Confirm Delete", "Delete this timetable row?"):
            status, data = api_request(
                "DELETE", f"/timetable/{item_id}"
            )
            if status == 200:
                messagebox.showinfo("Success", "Timetable deleted successfully!")
                load()
            else:
                show_backend_error(status, data, "Delete Timetable")

    make_action_buttons(content, add, edit, delete)
    load()


# ---------------- Attendance ----------------

def attendance():
    clear_content()
    title_lbl("Attendance", "Subject-wise attendance tracking")

    table = tk.Frame(content, bg=CARD)
    table.pack(fill="x", padx=25, pady=10)

    for i, text in enumerate(["Subject", "Percentage"]):
        tk.Label(
            table, text=text, font=("Arial", 11, "bold"),
            bg=PRIMARY, fg=WHITE, padx=25, pady=10
        ).grid(row=0, column=i, sticky="ew")

    try:
        response = requests.get(f"{API_BASE}/attendance", timeout=4)
        att_data = response.json()
        subjects = att_data.get("subjects", [])

        for r, subject in enumerate(subjects, 1):
            tk.Label(
                table, text=subject["name"], bg=WHITE, fg=TEXT,
                padx=25, pady=10
            ).grid(row=r, column=0, sticky="ew")
            tk.Label(
                table, text=f'{subject["percentage"]}%',
                bg=WHITE, fg=TEXT, padx=25, pady=10
            ).grid(row=r, column=1, sticky="ew")
    except Exception:
        tk.Label(
            table, text="Error fetching attendance data",
            bg=WHITE, fg="red", padx=25, pady=10
        ).grid(row=1, column=0, columnspan=2, sticky="ew")


# ---------------- AI Assistant ----------------

def ai_assistant():
    clear_content()
    title_lbl(
        "AI Study Assistant",
        "Ask your AI-powered study assistant"
    )

    chat = tk.Text(
        content, height=18, font=("Arial", 11),
        bg=WHITE, fg=TEXT, wrap="word", padx=12, pady=12
    )
    chat.pack(fill="both", expand=True, padx=25, pady=(5, 10))
    chat.insert("end", "AI: Hello! How can I help you?\n\n")
    chat.config(state="disabled")

    bottom = tk.Frame(content, bg="#f4f6fb")
    bottom.pack(fill="x", padx=25, pady=(0, 15))
    entry = tk.Entry(bottom, font=("Arial", 12))
    entry.pack(side="left", fill="x", expand=True, ipady=9)

    def send():
        q = entry.get().strip()
        if not q:
            return
        entry.delete(0, "end")
        chat.config(state="normal")
        chat.insert("end", f"You: {q}\n")
        try:
            res = requests.post(
                f"{API_BASE}/ai/chat",
                json={"message": q},
                timeout=8
            )
            ans = (
                res.json().get("response", "Error")
                if res.status_code == 200 else "Backend Error"
            )
            chat.insert("end", f"AI: {ans}\n\n")
        except Exception:
            chat.insert("end", "AI: Server Offline! Start main.py\n\n")
        chat.config(state="disabled")

    tk.Button(
        bottom, text="Send", command=send,
        bg=PRIMARY, fg=WHITE, font=("Arial", 11, "bold"),
        padx=22, pady=8
    ).pack(side="right", padx=(10, 0))


# ---------------- AI Doubt Solver ----------------

def ai_doubt_solver():
    clear_content()
    title_lbl(
        "AI Doubt Solver",
        "Type your question and get an AI explanation"
    )

    tk.Label(
        content, text="Enter your question:",
        font=("Arial", 12, "bold"), bg="#f4f6fb", fg=TEXT
    ).pack(anchor="w", padx=25)

    question = tk.Text(content, height=8, font=("Arial", 11))
    question.pack(fill="x", padx=25, pady=10)

    answer = tk.Label(
        content, text="AI answer will appear here...",
        font=("Arial", 11), bg=WHITE, fg=MUTED,
        anchor="nw", justify="left", padx=15, pady=15
    )
    answer.pack(fill="both", expand=True, padx=25, pady=5)

    def solve():
        q = question.get("1.0", "end").strip()
        if not q:
            messagebox.showwarning("Warning", "Please enter a question.")
            return

        try:
            response = requests.post(
                f"{API_BASE}/ai/chat",
                json={"message": q},
                timeout=8
            )
            ans_text = response.json().get("response", "")
            answer.config(text=f"AI Answer:\n\n{ans_text}")
        except Exception:
            answer.config(text="Error:\nBackend is not running.")

    tk.Button(
        content, text="Solve with AI", command=solve,
        bg=PRIMARY, fg=WHITE, font=("Arial", 11, "bold"),
        relief="flat", padx=20, pady=8
    ).pack(anchor="w", padx=25, pady=10)


# ---------------- Sidebar Navigation ----------------

sidebar = tk.Frame(root, bg=SIDEBAR, width=240)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(
    sidebar, text="COLLEGE APP",
    font=("Arial", 17, "bold"),
    bg=SIDEBAR, fg=WHITE
).pack(pady=(25, 20))


def btn(text, cmd):
    tk.Button(
        sidebar, text=text, command=cmd,
        font=("Arial", 11), bg=SIDEBAR, fg=WHITE,
        activebackground=PRIMARY, activeforeground=WHITE,
        relief="flat", anchor="w", padx=25, pady=9,
        cursor="hand2"
    ).pack(fill="x")


btn("Dashboard", dashboard)
btn("Students Database", profile)
btn("Register Student", register_page)
btn("Attendance", attendance)
btn("Assignments", assignments)
btn("Exams & Results", exams_results)
btn("Notices", notices)
btn("Timetable", timetable)

tk.Label(
    sidebar, text="AI FEATURES",
    font=("Arial", 9, "bold"),
    bg=SIDEBAR, fg="#9ca3af"
).pack(anchor="w", padx=25, pady=(20, 5))

btn("AI Assistant", ai_assistant)
btn("AI Doubt Solver", ai_doubt_solver)

# Main content
content = tk.Frame(root, bg="#f4f6fb")
content.pack(side="right", fill="both", expand=True)

dashboard()
root.mainloop()