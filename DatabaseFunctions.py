from datetime import datetime
import sqlite3

def create_user(name, email, card_number):
    conn = sqlite3.connect('swipe_system.db', timeout = 5)
    c = conn.cursor()

    # Ensure the users table exists
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        card_number TEXT UNIQUE NOT NULL
    )
    ''')

    try:
        # Insert new user
        c.execute('''
            INSERT INTO users (name, email, card_number)
            VALUES (?, ?, ?)
        ''', (name, email, card_number))
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


def log_check_in(card_number):
    conn = sqlite3.connect('swipe_system.db', timeout = 5)
    c = conn.cursor()

    # Find user by card_number
    c.execute('SELECT id, name FROM users WHERE card_number = ?', (card_number,))
    user = c.fetchone()

    if user:
        user_id, name = user
        now = datetime.now().isoformat(timespec='seconds')

        # Insert a new log entry with log_in_time and NULL log_out_time
        c.execute('INSERT INTO logs (user_id, log_in_time, log_out_time) VALUES (?, ?, NULL)', (user_id, now))
        conn.commit()
        
        print(f"{name} checked in at {now}")
        return "success"
    else:
        
        print("Card not recognized.")
        return "error"

    conn.close()


def log_check_out(card_number):
    conn = sqlite3.connect('swipe_system.db', timeout = 5)
    c = conn.cursor()

    # Find user by card_number
    c.execute('SELECT id, name FROM users WHERE card_number = ?', (card_number,))
    user = c.fetchone()

    if user:
        user_id, name = user
        now = datetime.now().isoformat(timespec='seconds')

        # Update the latest log entry for this user with NULL log_out_time
        c.execute('''
            UPDATE logs
            SET log_out_time = ?
            WHERE user_id = ? AND log_out_time IS NULL
            ORDER BY log_in_time DESC
            LIMIT 1
        ''', (now, user_id))
        
        if c.rowcount == 0:
            
            print("No active check-in found for this user.")
            return "no sesh"
        else:
            
            conn.commit()
            print(f"{name} checked out at {now}")
            return "success"
    else:
        
        print("Card not recognized.")
        return "error"

    conn.close()

def get_email(card_number):
    """
    Retrieves the email address associated with the given card number.
    Returns the email as a string, or None if not found.
    """
    conn = sqlite3.connect('swipe_system.db', timeout=5)
    c = conn.cursor()

    c.execute('SELECT email FROM users WHERE card_number = ?', (card_number,))
    result = c.fetchone()

    conn.close()

    if result:
        return result[0]  # email
    else:
        return None


def delete_user(identifier):
    """
    Deletes a user from the database using their email, card number, or name.
    """
    conn = sqlite3.connect('swipe_system.db', timeout=5)
    c = conn.cursor()

    # Try to match on email, card_number, or name
    c.execute('''
        DELETE FROM users
        WHERE email = ? OR card_number = ? OR name = ?
    ''', (identifier, identifier, identifier))

    conn.commit()
    
    if c.rowcount > 0:
        print(f"User '{identifier}' deleted successfully.")
        result = "success"
    else:
        print(f"No user found for identifier: {identifier}")
        result = "not found"

    conn.close()
    return result

def export_logs_to_text_file(output_file='user_logs.txt'):
    """
    Exports each user's check-in and check-out times to a text file.
    """
    conn = sqlite3.connect('swipe_system.db', timeout=5)
    c = conn.cursor()

    # Ensure logs table exists (optional safety)
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            log_in_time TEXT,
            log_out_time TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Join logs with user information
    c.execute('''
        SELECT u.name, u.email, l.log_in_time, l.log_out_time
        FROM logs l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.log_in_time ASC
    ''')
    
    logs = c.fetchall()
    conn.close()

    # Write to file
    with open(output_file, 'w') as f:
        f.write("User Check-In/Check-Out Report\n")
        f.write("="*40 + "\n\n")
        for name, email, log_in, log_out in logs:
            f.write(f"Name: {name}\n")
            f.write(f"Email: {email}\n")
            f.write(f"Check-in Time: {log_in}\n")
            f.write(f"Check-out Time: {log_out if log_out else 'N/A'}\n")
            f.write("-" * 40 + "\n")
    
    print(f"Logs exported to '{output_file}' successfully.")

export_logs_to_text_file()
