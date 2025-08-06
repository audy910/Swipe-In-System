import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import *
from DatabaseFunctions import create_admin, admin_exists, admin_user_exists
from sendEmail import send_email

# === DATABASE SETUP ===

# Connect to or create the database
conn = sqlite3.connect('swipe_system.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    card_number TEXT UNIQUE NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    log_in_time TEXT,
    log_out_time TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    card_number TEXT UNIQUE NOT NULL
)
''')


# === FUNCTIONS ===

def open_new_window(action):
    # Open a new window for admin creation or feedback.
    new_window = Toplevel(base)
    new_window.geometry("400x200")
    new_window.config(bg="#D6EAF8")
    new_window.title("Create Admin Account Confirmation")

    if action == "create":
        if admin_exists():
            # If admin already exists, notify and close after delay
            Label(
                new_window,
                text="Admin already exists!",
                font=("Helvetica", 14),
                fg='#333333',
                bg="#FCF3CF",
                width=40,
                height=5
            ).pack(pady=50)
            new_window.after(2000, new_window.destroy)
            return

        else: 
            # Prompt for card swipe
            entry_label = Label(
                new_window,
                text="Swipe ID Card",
                font=("Helvetica", 14),
                fg='#333333',
                bg="#FCF3CF",
                width=40,
                height=5
            )
            entry_label.pack(pady=50)

            card_input_var = StringVar()
            card_input_entry = Entry(
                new_window,
                font=("Helvetica", 14),
                fg='#333333',
                relief=SOLID,
                bd=0,
                width=30,
                textvariable=card_input_var
            )
            card_input_entry.place(x=-1000, y=-1000)  # Keep off-screen
            new_window.after(300, card_input_entry.focus_force)

            def process_swipe():
                #Handle card data and create admin.
                card_data = card_input_var.get().strip()
                print(f"Raw swipe data: '{card_data}'")
                card_data = card_data.replace(";", "").replace("?", "").split("=")[0]
                print(f"Cleaned card data: '{card_data}'")

                if card_data == "E" or not card_data:
                    entry_label.config(text="Please Try Again!", bg="#FFB6C1")
                    card_input_var.set("")
                    return

                result = create_admin(name_value, email_value, card_data)
                if result == "success":
                    entry_label.config(text="Admin Created Successfully!", bg="#A3E4D7")
                    email_body = f"Your admin account has been created as:\n\nName: {name_value}\nEmail: {email_value}"
                    send_email("Admin Account Created", email_body, email_value)
                else:
                    entry_label.config(text="Error Occurred, please try again!", bg="#A3E4D7")

                new_window.after(2000, new_window.destroy)
                card_input_var.set("")

            card_input_entry.bind("<Return>", lambda event: new_window.after(100, process_swipe))
    elif action == "add":
        entry_label = Label(
            new_window,
            text="Swipe Registered Admin Card to proceed",
            font=("Helvetica", 14),
            fg='#333333',
            bg="#FCF3CF",
            width=40,
            height=5
        )
        entry_label.pack(pady=50)

        card_input_var = StringVar()
        card_input_entry = Entry(
            new_window,
            font=("Helvetica", 14),
            fg='#333333',
            relief=SOLID,
            bd=0,
            width=30,
            textvariable=card_input_var
        )
        card_input_entry.place(x=-1000, y=-1000)  # Keep off-screen
        new_window.after(300, card_input_entry.focus_force)

        # Track swipe stage
        swipe_stage = {"step": "authorize"}

        def process_swipe():
            card_data = card_input_var.get().strip()
            print(f"Raw swipe data: '{card_data}'")
            card_data = card_data.replace(";", "").replace("?", "").split("=")[0]
            print(f"Cleaned card data: '{card_data}'")

            if card_data == "E" or not card_data:
                entry_label.config(text="Please Try Again!", bg="#FFB6C1")
                card_input_var.set("")
                return

            if swipe_stage["step"] == "authorize":
                if admin_user_exists(card_data):
                    entry_label.config(text="Authorized! Now swipe new admin card.", bg="#A3E4D7")
                    swipe_stage["step"] = "register"
                    card_input_var.set("")
                else:
                    entry_label.config(text="Unauthorized card. Try again.", bg="#FFB6C1")
                    card_input_var.set("")
            elif swipe_stage["step"] == "register":
                result = create_admin(name_value, email_value, card_data)
                if result == "success":
                    entry_label.config(text="New Admin Created!", bg="#A3E4D7")
                    email_body = f"Your admin account has been created as:\n\nName: {name_value}\nEmail: {email_value}"
                    send_email("Admin Account Created", email_body, email_value)
                else:
                    entry_label.config(text="Error occurred. Try again.", bg="#FFB6C1")
                new_window.after(2000, new_window.destroy)

            card_input_var.set("")

        card_input_entry.bind("<Return>", lambda event: new_window.after(100, process_swipe))






def submit():
    # Submit name and email to create admin.
    global name_value, email_value
    name_value = name_entry.get()
    email_value = email_entry.get()
    open_new_window("create")


def add_admin():
    #Alternative flow to add admin 
    global name_value, email_value
    name_value = name_entry.get()
    email_value = email_entry.get()
    open_new_window("add")


# === GUI SETUP ===

base = Tk()
base.geometry("800x480")
base.eval('tk::PlaceWindow . center')
base.title("Swipe In System")
base.config(bg="#F5F5F5")

# Main UI container
canvas = tk.Frame(base, bg='white', bd=5, relief='ridge')
canvas.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.85, relheight=0.8)

# UI Elements
Label(canvas, text="Create Admin Account", font=("Helvetica", 20, "bold"),
      bg='#FFFFFF', fg='#333333').pack(pady=10)

Label(canvas, text="Enter Name", font=("Helvetica", 14),
      bg='#FFFFFF', fg='#555555').pack(pady=10)
name_entry = Entry(canvas, font=("Helvetica", 14), relief=SOLID, bd=2,
                   fg='#333333', highlightthickness=2, highlightcolor='#FF8C8C')
name_entry.pack(pady=10)

Label(canvas, text="Enter Email", font=("Helvetica", 14),
      bg='#FFFFFF', fg='#555555').pack(pady=10)
email_entry = Entry(canvas, font=("Helvetica", 14), relief=SOLID, bd=2,
                    fg='#333333', highlightthickness=2, highlightcolor='#FF8C8C')
email_entry.pack(pady=10)

# Buttons
Button(canvas, text="SUBMIT", command=submit, font=("Helvetica", 14, "bold"),
       bg='#D6EAF8', fg='black', relief=FLAT, bd=0, activebackground='#FCF3CF').pack(pady=10)

Button(canvas, text="Add Admin", command=add_admin, font=("Helvetica", 14, "bold"),
       bg='#D6EAF8', fg='black', relief=FLAT, bd=0, activebackground='#FCF3CF').pack(pady=10)


# === START APP ===

base.mainloop()
conn.commit()
conn.close()
print("Database and tables created successfully!")
