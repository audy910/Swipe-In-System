import tkinter as tk
from tkinter import *
from tkinter import ttk
from datetime import datetime

from sendEmail import send_email, send_logs
from DatabaseFunctions import (
    create_user, log_check_in, log_check_out,
    get_email, delete_user, admin_user_exists, 
    get_admin_email
)

# === GLOBAL VARIABLES ===
name_value = ""
email_value = ""
sid_value = ""

# === CARD SWIPE PROCESSING ===
def open_new_window(action):
    new_window = Toplevel(base)
    new_window.geometry("400x200")
    new_window.config(bg="#D6EAF8")
    new_window.title("Read Card Swipe")

    entry_label = Label(
        new_window, text="Swipe R'Card",
        font=("Helvetica", 16), fg='#333333',
        bg="#FCF3CF", width=40, height=5
    )
    entry_label.pack(pady=50)

    card_input_var = StringVar()
    card_input_entry = Entry(
        new_window, font=("Helvetica", 16), fg='#333333',
        relief=SOLID, bd=0, width=30, textvariable=card_input_var
    )
    card_input_entry.place(x=-1000, y=-1000)
    new_window.after(300, card_input_entry.focus_force)

    def process_swipe():
        card_data = card_input_var.get().strip()
        print(f"Raw swipe data: '{card_data}'")

        card_data = card_data.replace(";", "").replace("?", "").split("=")[0]
        print(f"Cleaned card data: '{card_data}'")

        if card_data == "E" or not card_data:
            entry_label.config(text="Please Try Again!", bg="#FFB6C1")
            card_input_var.set("")
            return

        # === CREATE USER ===
        if action == "create":
            result = create_user(name_value, email_value, sid_value, card_data)
            print("Create user result:", result)

            if result == "success":
                entry_label.config(text="Your card has been recorded!", bg="#A3E4D7")
                email_body = f"Your user account has been created:\n\nName: {name_value}\nEmail: {email_value}\nSID: {sid_value}"
                send_email("Account Created", email_body, email_value)

            elif result == "card error":
                entry_label.config(text="Card already exists!", bg="#FF9494")

            elif result == "email error":
                entry_label.config(text="Email already exists!", bg="#FF9494")

            elif result == "sid error":
                entry_label.config(text="SID already exists!", bg="#FF9494")

            else:
                entry_label.config(text="Unknown error occurred!", bg="#FF9494")

        # === CHECK IN ===
        elif action == "in":
            result = log_check_in(card_data, box_value)
            print("Check-in result:", result)

            if result == "success":
                now = datetime.now().isoformat(timespec='seconds')
                entry_label.config(text=f"Box #{box_value} has been checked out!", bg="#A3E4D7")
                send_email("Check Out Box", f"You checked out Box #{box_value} at: {now}", get_email(card_data))

            elif result == "already_checked_in":
                entry_label.config(text="You must return your previous box first!", bg="#FF9494")

            else:
                entry_label.config(text="Card not recognized!", bg="#FF9494")

        # === CHECK OUT ===
        elif action == "out":
            result = log_check_out(card_data)
            print("Check-out result:", result)

            if result == "success":
                now = datetime.now().isoformat(timespec='seconds')
                entry_label.config(text="Box returned!", bg="#A3E4D7")
                send_email("Box Returned", f"You returned a box at: {now}", get_email(card_data))

            elif result == "no sesh":
                entry_label.config(text="You do not have any checked-out box!", bg="#FF9494")

            else:
                entry_label.config(text="Card not recognized!", bg="#FF9494")

        # === DELETE USER ===
        elif action == "delete":
            result = delete_user(card_data)
            print("Delete result:", result)

            if result == "success":
                entry_label.config(text="Your account has been deleted!", bg="#A3E4D7")
            else:
                entry_label.config(text="Account not found!", bg="#FF9494")

        # === EMAIL LOGS ===
        elif action == "email_logs":
            if admin_user_exists(card_data):
                entry_label.config(text="Emailing logs...", bg="#A3E4D7")
                send_logs("Logs", "Attached are the logs.", get_admin_email(card_data))
                entry_label.config(text="Logs emailed!", bg="#A3E4D7")
            else:
                entry_label.config(text="Admin card not recognized!", bg="#FF9494")

        new_window.after(2000, new_window.destroy)

    card_input_entry.bind("<Return>", lambda event: new_window.after(100, process_swipe))

# === BUTTON HANDLERS ===
def check_in():
    global box_value
    box_value = box_entry.get()
    if not box_value.isdigit():
        return
    open_new_window("in")

def check_out():
    open_new_window("out")

def delete_account():
    open_new_window("delete")

def email_logs():
    open_new_window("email_logs")

def submit():
    global name_value, email_value, sid_value
    name_value = name_entry.get()
    email_value = email_entry.get()
    sid_value = sid_entry.get()
    open_new_window("create")

# === GUI SETUP ===
base = tk.Tk()
base.geometry("750x400")
base.title("Swipe In System")
base.config(bg="#F5F5F5")

canvas = tk.Frame(base, bg='white', bd=5, relief='ridge')
canvas.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.85, relheight=0.8)
canvas.grid_columnconfigure(0, weight=1)
canvas.grid_columnconfigure(1, weight=1)

# Registered Users Section
Label(canvas, text="Registered Users", font=("Helvetica", 20, "bold"),
      bg='#FFFFFF', fg='#333333').grid(row=1, column=0, pady=5, padx=30)

# Check Out box
Button(canvas, text="Check Out Box", command=check_in, font=("Helvetica", 16, "bold"),
       bg='#D6EAF8', fg='black', relief=FLAT).grid(row=4, column=0, pady=5, padx=30)

# Box number entry
Label(canvas, text="Box Number", font=("Helvetica", 14),
      bg='#FFFFFF', fg='#555555').grid(row=2, column=0, pady=1, padx=30)
box_entry = Entry(canvas, font=("Helvetica", 14), relief=SOLID, bd=2,
                    fg='#333333')
box_entry.grid(row=3, column=0, pady=1, padx=30)

# Return box
Button(canvas, text="Return Box", command=check_out, font=("Helvetica", 16, "bold"),
       bg='#D6EAF8', fg='black', relief=FLAT).grid(row=5, column=0, pady=5, padx=30)

# Delete account
Button(canvas, text="Delete Account", command=delete_account, font=("Helvetica", 14, "bold"),
       bg='#F9E79F', fg='black', relief=FLAT).grid(row=8, column=0, pady=5, padx=40)

# Export logs
Button(canvas, text="Export Logs", command=email_logs, font=("Helvetica", 14, "bold"),
       bg='#D6EAF8', fg='black', relief=FLAT).grid(row=7, column=0, pady=5, padx=40)

# Create Account header
Label(canvas, text="Create Account", font=("Helvetica", 20, "bold"),
      bg='#FFFFFF', fg='#333333').grid(row=1, column=1, pady=1, padx=30)

# name
Label(canvas, text="Enter Name", font=("Helvetica", 14),
      bg='#FFFFFF').grid(row=2, column=1, pady=1, padx=30)
name_entry = Entry(canvas, font=("Helvetica", 14), relief=SOLID, bd=2)
name_entry.grid(row=3, column=1, pady=1, padx=30)

# email
Label(canvas, text="Enter Student Email", font=("Helvetica", 14),
      bg='#FFFFFF').grid(row=4, column=1, pady=1, padx=30)
email_entry = Entry(canvas, font=("Helvetica", 14), relief=SOLID, bd=2)
email_entry.grid(row=5, column=1, pady=1, padx=30)

# SID
Label(canvas, text="Enter SID", font=("Helvetica", 14),
      bg='#FFFFFF').grid(row=6, column=1, pady=1, padx=30)
sid_entry = Entry(canvas, font=("Helvetica", 14), relief=SOLID, bd=2)
sid_entry.grid(row=7, column=1, pady=1, padx=30)

# submit
Button(canvas, text="SUBMIT", command=submit, font=("Helvetica", 14, "bold"),
       bg='#D6EAF8', fg='black', relief=FLAT).grid(row=8, column=1, pady=1, padx=40)

# Start
base.mainloop()
