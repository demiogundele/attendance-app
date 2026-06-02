from flask import Flask, render_template, request, redirect, url_for, session
from database import get_all_children, add_child, init_db, save_attendance, get_attendance_history, get_attendance_by_date, delete_child, delete_all_children, delete_class_group, update_child, check_password 
from datetime import date 
import csv
import io 

CLASSES = [
    "God's Heritage (0-6)", 
    "Chosen Generation (6-10)",
    "Royal Preteens (11-13)",
    "Teen Church (13-18)"
]

app = Flask(__name__)
app.secret_key = "church-secret-key-2026"

def is_logged_in():
    return session.get("logged_in") == True

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        password = request.form.get("password")
        if check_password(password):
            session["logged_in"] = True
            return redirect(url_for("home"))
        else: 
            error = "Incorrect password. Please try again."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.before_request
def setup():
    init_db()

@app.route('/')
def home():
    if not is_logged_in():
        return redirect(url_for("login"))
    return render_template('home.html')

@app.route('/attendance')
def index():
    if not is_logged_in():
        return redirect(url_for("login"))
    kids = get_all_children()
    today = date.today().isoformat()
    return render_template('index.html', kids=kids, today=today, classes=CLASSES)

@app.route('/submit_attendance', methods=["POST"])
def submit_attendance():
    if not is_logged_in():
        return redirect(url_for("login"))
    session_date = request.form.get("session_date")
    present_ids = request.form.getlist("present")
    save_attendance(session_date, present_ids)
    return redirect(url_for("history"))

@app.route("/roster", methods=["GET", "POST"])
def roster():
    if not is_logged_in():
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form.get("name").strip()
        class_group = request.form.get("class_group")
        if name and class_group: 
            add_child(name, class_group)
    kids = get_all_children()
    return render_template("roster.html", kids=kids, classes=CLASSES)
    
@app.route("/history")
def history():
    if not is_logged_in():
        return redirect(url_for("login"))
    rows = get_attendance_history()
    return render_template("history.html", rows=rows)

@app.route("/export_csv/<session_date>")
def export_csv(session_date): 
    if not is_logged_in():
        return redirect(url_for("login"))
    rows = get_attendance_by_date(session_date)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Class", "Attendance"])
    for row in rows: 
        writer.writerow([row["name"], row["class_group"], "Present" if row["present"] else "Absent"])
    output.seek(0)
    return app.response_class(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=attendance_{session_date}.csv"}
    )

@app.route("/delete_child/<int:child_id>", methods=["POST"])
def remove_child(child_id):
    if not is_logged_in():
        return redirect(url_for("login"))
    delete_child(child_id)
    return redirect(url_for("roster"))

@app.route("/delete_all", methods=["POST"])
def remove_all():
    if not is_logged_in():
        return redirect(url_for("login"))
    delete_all_children()
    return redirect(url_for("roster"))

@app.route("/delete_class/<class_group>", methods=["POST"])
def remove_class(class_group):
    if not is_logged_in():
        return redirect(url_for("login"))
    delete_class_group(class_group)
    return redirect(url_for("roster"))

@app.route("/edit_child/<int:child_id>", methods=["POST"])
def edit_child(child_id):
    if not is_logged_in():
        return redirect(url_for("login"))
    if request.method == "POST":
        new_name = request.form.get("name").strip()
        new_class = request.form.get("class_group")
        if new_name and new_class: 
            update_child(child_id, new_name, new_class)
        return redirect(url_for("roster"))
    kids = get_all_children()
    kid = next((k for k in kids if k["id"] == child_id), None) 
    return render_template("edit_child.html", kid=kid, classes=CLASSES)

if __name__ == "__main__":
    app.run(debug=True)
