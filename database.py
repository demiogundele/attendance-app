import sqlite3

DB = 'attendance.db'

def get_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.executescript('''
CREATE TABLE IF NOT EXISTS children (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    class_group TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER REFERENCES children(id),
    session TEXT NOT NULL, 
    present INTEGER DEFAULT 0
);
''')
    conn.commit()
    conn.close()

def get_all_children():
    conn = get_connection()
    kids = conn.execute("SELECT * FROM children ORDER BY name").fetchall()
    conn.close()
    return kids

def add_child(name, class_group):
    conn = get_connection()
    conn.execute("INSERT INTO children (name, class_group) VALUES (?, ?)", (name, class_group))
    conn.commit()
    conn.close()

def save_attendance(session_date, present_ids):
    conn = get_connection()
    kids = conn.execute("SELECT id FROM children").fetchall()
    for kid in kids: 
        present = 1 if str(kid["id"]) in present_ids else 0
        existing = conn.execute(
            "SELECT id FROM attendance WHERE child_id=? AND session=?",
            (kid["id"], session_date)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE attendance SET present=? WHERE child_id=? AND session=?",
                (present, kid["id"], session_date)
            )
        else: 
            conn.execute(
                "INSERT INTO attendance (child_id, session, present) VALUES (?, ?, ?)",
                (kid["id"], session_date, present)                     
            )
    conn.commit()
    conn.close()
    
def get_attendance_history():
    conn = get_connection()
    rows = conn.execute('''
        SELECT c.name, c.class_group,a.session, a.present
        FROM attendance a
        JOIN children c ON c.id = a.child_id
        ORDER BY a.session DESC, c.class_group,c.name
    ''').fetchall()
    conn.close()
    return rows

def get_attendance_by_date(session_date): 
    conn = get_connection()
    rows = conn.execute('''
        SELECT c.name, c.class_group, a.present
        FROM attendance a 
        JOIN children c ON c.id = a.child_id 
        WHERE a.session = ?
        ORDER BY c.class_group, c.name 
    ''', (session_date,)).fetchall()
    conn.close()
    return rows 

def delete_child(child_id): 
    conn = get_connection()
    conn.execute("DELETE FROM attendance WHERE child_id=?", (child_id,))
    conn.execute("DELETE FROM children WHERE id=?", (child_id,))
    conn.commit()
    conn.close()

def delete_all_children(): 
    conn = get_connection()
    conn.execute("DELETE FROM attendance")
    conn.execute("DELETE FROM children")
    conn.commit()
    conn.close()

def delete_class_group(class_group): 
    conn = get_connection()
    kids = conn.execute("SELECT id FROM children WHERE class_group=?", (class_group,)).fetchall()
    for kid in kids: 
        conn.execute("DELETE FROM attendance WHERE child_id=?", (kid["id"],))
    conn.execute("DELETE FROM children WHERE class_group=?", (class_group,))
    conn.commit()
    conn.close()

def check_password(password): 
    return password == "AGP123"

def update_child(child_id, new_name, new_class): 
    conn = get_connection()
    conn.execute(
        "UPDATE children SET name=?, class_group=? WHERE id=?",
        (new_name, new_class, child_id)
    )
    conn.commit()
    conn.close() 
    