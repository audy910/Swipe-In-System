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

        if action == "create":
            result = create_user(name_value, email_value, card_data)
            print("Create user result:", result)

            if result == "success":
                entry_label.config(text="Your card has been recorded!", bg="#A3E4D7")
                email_body = f"Your account has been created as:\n\nName: {name_value}\nEmail: {email_value}"
                send_email("Account Created", email_body, email_value)
            elif result == "card error":
                entry_label.config(text="Card already exists!", bg="#A3E4D7")
            elif result == "email error":
                entry_label.config(text="Email already exists!", bg="#A3E4D7")
            else:
                entry_label.config(text="An error occurred, please try again!", bg="#A3E4D7")

        elif action == "in":
            result = log_check_in(card_data)
            print("Check-in result:", result)

            if result == "success":
                now = datetime.now().isoformat(timespec='seconds')
                entry_label.config(text="You have been checked in!", bg="#A3E4D7")
                send_email("Check In", f"You checked in at: {now}", get_email(card_data))
            else:
                entry_label.config(text="Card not recognized, please try again!", bg="#A3E4D7")

        elif action == "out":
            result = log_check_out(card_data)
            print("Check-out result:", result)

            if result == "success":
                now = datetime.now().isoformat(timespec='seconds')
                entry_label.config(text="You have been checked out!", bg="#A3E4D7")
                send_email("Check Out", f"You checked out at: {now}", get_email(card_data))
            elif result == "no sesh":
                entry_label.config(text="No session found, please check in!", bg="#A3E4D7")
            else:
                entry_label.config(text="Card not recognized, please try again!", bg="#A3E4D7")

        elif action == "delete":
            result = delete_user(card_data)
            print("Delete account result:", result)

            if result == "success":
                entry_label.config(text="Your account has been deleted!", bg="#A3E4D7")
            else:
                entry_label.config(text="No account found!", bg="#A3E4D7")

        elif action == "email_logs":
            if admin_user_exists(card_data):
                entry_label.config(text="Emailing logs...", bg="#A3E4D7")
                print(get_admin_email(card_data))
                send_logs("Logs", "Attached are the logs for your account:\n\n", get_admin_email(card_data))
                entry_label.config(text="Logs emailed successfully!", bg="#A3E4D7")

        new_window.after(2000, new_window.destroy)

    card_input_entry.bind("<Return>", lambda event: new_window.after(100, process_swipe))

# === BUTTON HANDLERS ===
def check_in():
    open_new_window("in")

def check_out():
    open_new_window("out")

def delete_account():
    open_new_window("delete")

def email_logs():
    open_new_window("email_logs")

def submit():
    global name_value, email_value
    name_value = name_entry.get()
    email_value = email_entry.get()
    open_new_window("create")

# === GUI SETUP ===
base = tk.Tk()
base.geometry("800x480")
base.eval('tk::PlaceWindow . center')
base.title("Swipe In System")
base.config(bg="#F5F5F5")

canvas = tk.Frame(base, bg='white', bd=5, relief='ridge')
canvas.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.85, relheight=0.8)
canvas.grid_columnconfigure(0, weight=1)
canvas.grid_columnconfigure(1, weight=1)

# Registered Users Section
Label(canvas, text="Registered Users", font=("Helvetica", 20, "bold"),
      bg='#FFFFFF', fg='#333333').grid(row=1, column=0, pady=10, padx=30)

Button(canvas, text="Check In", command=check_in, font=("Helvetica", 16, "bold"),
       bg='#D6EAF8', fg='black', relief=FLAT, bd=0, activebackground='#FCF3CF'
).grid(row=2, column=0, pady=10, padx=30)

Button(canvas, text="Check Out", command=check_out, font=("Helvetica", 16, "bold"),
       bg='#D6EAF8', fg='black', relief=FLAT, bd=0, activebackground='#FCF3CF'
).grid(row=3, column=0, pady=10, padx=30)

# Create Account Section
Label(canvas, text="Create Account", font=("Helvetica", 20, "bold"),
      bg='#FFFFFF', fg='#333333').grid(row=1, column=1, pady=10, padx=30)

Label(canvas, text="Enter Name", font=("Helvetica", 14),
      bg='#FFFFFF', fg='#555555').grid(row=2, column=1, pady=10, padx=30)

name_entry = Entry(canvas, font=("Helvetica", 16), relief=SOLID, bd=2,
                   fg='#333333', highlightthickness=2, highlightcolor='#FF8C8C')
name_entry.grid(row=3, column=1, pady=10, padx=30)

Label(canvas, text="Enter Email", font=("Helvetica", 14),
      bg='#FFFFFF', fg='#555555').grid(row=4, column=1, pady=10, padx=30)

email_entry = Entry(canvas, font=("Helvetica", 16), relief=SOLID, bd=2,
                    fg='#333333', highlightthickness=2, highlightcolor='#FF8C8C')
email_entry.grid(row=5, column=1, pady=10, padx=30)

Button(canvas, text="SUBMIT", command=submit, font=("Helvetica", 14, "bold"),
       bg='#D6EAF8', fg='black', relief=FLAT, bd=0, activebackground='#FCF3CF'
).grid(row=6, column=1, pady=10, padx=40, ipadx=5, ipady=5)

Button(canvas, text="Delete Account", command=delete_account, font=("Helvetica", 14, "bold"),
       bg='#F9E79F', fg='black', relief=FLAT, bd=0, activebackground='#FAB8AF'
).grid(row=6, column=0, pady=10, padx=40, ipadx=5, ipady=5)

Button(canvas, text="Export Logs", command=email_logs, font=("Helvetica", 14, "bold"),
       bg='#D6EAF8', fg='black', relief=FLAT, bd=0, activebackground='#FCF3CF'
).grid(row=5, column=0, pady=10, padx=40)

# === START APPLICATION ===
base.mainloop()
