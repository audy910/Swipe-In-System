from datetime import datetime
import sqlite3
def create_user(name, email, card_number, sid):
    conn = sqlite3.connect('swipe_system.db', timeout=5)
    c = conn.cursor()

    # Ensure the users table exists
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        sid TEXT UNIQUE NOT NULL,
        card_number TEXT UNIQUE NOT NULL
    )
    ''')

    try:
        # Insert new user
        c.execute('''
            INSERT INTO users (name, email, card_number, sid)
            VALUES (?, ?, ?, ?)
        ''', (name, email, card_number, sid))
        conn.commit()
        
        print(f"User '{name}' created successfully.")
        return "success"
    except sqlite3.IntegrityError as e:
        if 'email' in str(e):
            print("Error: This email is already registered.")
            return "email error"
        elif 'card_number' in str(e):
            print("Error: This card number is already in use.")
            return "card error"
        else:
            print(f"Database error: {e}")
            return "error"
    finally:
        conn.close()

def log_check_in(card_number, box):
    conn = sqlite3.connect('swipe_system.db', timeout=5)
    c = conn.cursor()

    try:
        card_number = card_number.strip()

        # Fetch user
        c.execute('SELECT id, name, sid FROM users WHERE card_number = ?', (card_number,))
        user = c.fetchone()

        if not user:
            print("Card not recognized.")
            return "error"

        user_id, name, sid = user

        # Check active session
        c.execute('SELECT id FROM logs WHERE user_id = ? AND log_out_time IS NULL', (user_id,))
        active_log = c.fetchone()

        if active_log:
            return "already_checked_in"

        # Insert new log (includes SID)
        now = datetime.now().isoformat(timespec='seconds')
        c.execute('''
            INSERT INTO logs (user_id, sid, box, log_in_time, log_out_time)
            VALUES (?, ?, ?, ?, NULL)
        ''', (user_id, sid, box, now))

        # Write row to Google Sheet
        sheet_row = write_row_to_sheet([
            name,      # col 1
            box,       # col 2
            email,     # col 3
            sid,       # col 4
            now,       # col 5 (checkout)
            ""         # col 6 (return empty)
        ])

        # Save row number to logs table
        c.execute("""
            INSERT INTO logs (user_id, sid, box, log_in_time, log_out_time, sheet_row)
            VALUES (?, ?, ?, ?, NULL, ?)
        """, (user_id, sid, box, now, sheet_row))


        conn.commit()
        print(f"{name} checked in at {now}")
        return "success"

    finally:
        conn.close()


def log_check_out(card_number):
    conn = sqlite3.connect('swipe_system.db', timeout=5)
    c = conn.cursor()

    try:
        card_number = card_number.strip()

        # Find user by card number
        c.execute('SELECT id, name FROM users WHERE card_number = ?', (card_number,))
        user = c.fetchone()

        if not user:
            print("Card not recognized.")
            return "error"

        user_id, name = user
        now = datetime.now().isoformat(timespec='seconds')

        # Find active log session
        c.execute('''
            SELECT id FROM logs
            WHERE user_id = ? AND log_out_time IS NULL
            ORDER BY log_in_time DESC
            LIMIT 1
        ''', (user_id,))
        log_entry = c.fetchone()

        if not log_entry:
            print("No active check-in found for this user.")
            return "no sesh"

        log_id = log_entry[0]

        # Update log-out time
        c.execute('''
            UPDATE logs
            SET log_out_time = ?
            WHERE id = ?
        ''', (now, log_id))

        log_id = log_entry[0]

        # Get sheet row number
        c.execute("SELECT sheet_row FROM logs WHERE id = ?", (log_id,))
        sheet_row = c.fetchone()[0]

        # Update Google Sheet
        update_return_date(sheet_row, now)

        conn.commit()
        print(f"{name} checked out at {now}")
        return "success"

    finally:
        conn.close()

def get_email(card_number):
    conn = sqlite3.connect('swipe_system.db', timeout=5)
    c = conn.cursor()

    try:
        c.execute('SELECT email FROM users WHERE card_number = ?', (card_number.strip(),))
        row = c.fetchone()
        return row[0] if row else None

    finally:
        conn.close()

def get_admin_email(card_number):
    conn = sqlite3.connect('swipe_system.db', timeout=5)
    c = conn.cursor()

    try:
        c.execute('SELECT email FROM admin WHERE card_number = ?', (card_number.strip(),))
        row = c.fetchone()
        return row[0] if row else None

    finally:
        conn.close()

def delete_user(identifier):
    conn = sqlite3.connect('swipe_system.db', timeout=5)
    c = conn.cursor()

    try:
        identifier = identifier.strip()
        c.execute("""
            DELETE FROM users
            WHERE email = ? OR card_number = ? OR name = ?
        """, (identifier, identifier, identifier))

        conn.commit()
        return "success" if c.rowcount > 0 else "not found"

    finally:
        conn.close()

def export_logs_to_text_file(output_file='user_logs.txt'):
    conn = sqlite3.connect('swipe_system.db', timeout=5)
    c = conn.cursor()

    try:
        c.execute("""
            SELECT u.name, u.email, l.log_in_time, l.log_out_time
            FROM logs l
            JOIN users u ON l.user_id = u.id
            ORDER BY l.log_in_time ASC
        """)
        rows = c.fetchall()

    finally:
        conn.close()

    # write file outside DB block
    with open(output_file, 'w') as f:
        f.write("User Check-In/Check-Out Report\n")
        f.write("=" * 40 + "\n\n")
        for name, email, log_in, log_out in rows:
            f.write(f"Name: {name}\n")
            f.write(f"Email: {email}\n")
            f.write(f"Check-in Time: {log_in}\n")
            f.write(f"Check-out Time: {log_out or 'N/A'}\n")
            f.write("-" * 40 + "\n")

def create_admin(name, email, card_number):
    conn = sqlite3.connect('swipe_system.db', timeout = 5)
    c = conn.cursor()

    # Ensure the users table exists
    c.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        card_number TEXT UNIQUE NOT NULL
    )
    ''')

    try:
        # Insert new user
        c.execute('''
            INSERT INTO admin (name, email, card_number)
            VALUES (?, ?, ?)
        ''', (name, email, card_number))
        conn.commit()
        
        print(f"Admin '{name}' created successfully.")
        return "success"
    except sqlite3.IntegrityError as e:
        if 'email' in str(e):
            
            print("Error: This email is already registered.")
            return "email error"
        elif 'card_number' in str(e):
            
            print("Error: This card number is already in use.")
            return "card error"
        else:
            
            print(f"Database error: {e}")
            return "error"
    finally:
        conn.close()

def admin_exists():
    conn = sqlite3.connect('swipe_system.db')
    c = conn.cursor()
    
    try:
        c.execute('SELECT COUNT(*) FROM admin')
        count = c.fetchone()[0]
        
        if count > 0:
            return True  # Admins exist
        else:
            return False  # No admin in table yet
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False  # Assume none exist if there's an error
    finally:
        conn.close()

def export_tables_to_text_files(db_path='swipe_system.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    tables = ['users', 'logs', 'admin']

    try:
        for table in tables:
            # Fetch all data
            c.execute(f"SELECT * FROM {table}")
            rows = c.fetchall()

            # Fetch column names
            col_names = [description[0] for description in c.description]

            # Write to text file
            with open(f"{table}_export.txt", 'w', encoding='utf-8') as f:
                f.write('\t'.join(col_names) + '\n')  # Header
                for row in rows:
                    f.write('\t'.join(str(item) if item is not None else '' for item in row) + '\n')

            print(f"Exported table '{table}' to {table}_export.txt")

        return "export success"

    except sqlite3.Error as e:
        print(f"Error exporting tables: {e}")
        return "export failed"
    finally:
        conn.close()


def admin_user_exists(card_number, db_path='swipe_system.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        c.execute('SELECT 1 FROM admin WHERE card_number = ?', (card_number,))
        return c.fetchone() is not None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

        
def get_user_info(card_number):
    conn = sqlite3.connect('swipe_system.db', timeout=5)
    c = conn.cursor()
    try:
        c.execute("SELECT name, email, sid FROM users WHERE card_number = ?", (card_number.strip(),))
        row = c.fetchone()
        return row if row else ("Unknown", "Unknown", "Unknown")
    finally:
        conn.close()


