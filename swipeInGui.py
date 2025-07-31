from tkinter import *
from tkinter import ttk
import tkinter as tk
from datetime import datetime
from sendEmail import send_email
from DatabaseFunctions import create_user, log_check_in, log_check_out, get_email, delete_user

# Global variables to store user details
name_value = ""
email_value = ""


    # Function to process card swipe
def open_new_window(action):
    new_window = Toplevel(base)
    new_window.geometry("400x200")
    new_window.config(bg="#D6EAF8")
    new_window.title("Check-in/Check-out Confirmation")

    entry_label = Label(new_window, text="Swipe R'Card", 
                        font=("Helvetica", 16), fg='#333333', bg="#FCF3CF", width=40, height=5)
    entry_label.pack(pady=50)

    card_input_var = StringVar()
    card_input_entry = Entry(new_window, font=("Helvetica", 16), fg='#333333', show="",
                             relief=SOLID, bd=0, width=30, textvariable=card_input_var)
    card_input_entry.place(x=-1000, y=-1000)  # Keep it off-screen

    # Ensure focus with slight delay to avoid focus issues
    new_window.after(300, lambda: card_input_entry.focus_force())

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
            code = create_user(name_value, email_value, card_data)
            print("Create user result:", code)
            if code == "success":
                entry_label.config(text="Your card has been recorded!", bg="#A3E4D7")
                email_body = f"Your account has been created as:\n\nName: {name_value}\nEmail: {email_value}"
                send_email("Account Created", email_body, email_value)
            elif code == "card error":
                entry_label.config(text="Card already exists!", bg="#A3E4D7")
            elif code == "email error":
                entry_label.config(text="Email already exists!", bg="#A3E4D7")
            else:
                entry_label.config(text="An Error has Occurred, please try again!", bg="#A3E4D7")

        elif action == "in":
            code = log_check_in(card_data)
            print("Check-in result code:", code)
            if code == "success":
                entry_label.config(text="You have been checked in!", bg="#A3E4D7")
                now = datetime.now().isoformat(timespec='seconds')
                email_body = f"You checked in at: {now}"
                email_account = get_email(card_data)
                send_email("Check In", email_body, email_account)
            else:
                entry_label.config(text="Card not recognized, please try again!", bg="#A3E4D7")

        elif action == "out":
            code = log_check_out(card_data)
            print("Check-out result code:", code)
            if code == "success":
                entry_label.config(text="You have been checked out!", bg="#A3E4D7")
                now = datetime.now().isoformat(timespec='seconds')
                email_body = f"You checked out at: {now}"
                email_account = get_email(card_data)
                send_email("Check Out", email_body, email_account)
            elif code == "no sesh":
                entry_label.config(text="No session found, please check in!", bg="#A3E4D7")
            else:
                entry_label.config(text="Card not recognized, please try again!", bg="#A3E4D7")

        elif action == "delete":
            code = delete_user(card_data)
            print("Delete account result code:", code)
            if code == "success":
                entry_label.config(text="Your account has been deleted!", bg="#A3E4D7")
            else:
                entry_label.config(text="No Account Found!", bg="#A3E4D7")

        # Clear and close after 2 seconds
        new_window.after(2000, lambda: new_window.destroy())

    # Bind only Enter key to trigger swipe processing
    card_input_entry.bind("<Return>", lambda event: new_window.after(100, process_swipe))

# Function to simulate check-in/check-out and log the timestamp
def checkIn():
    open_new_window("in")
    
def checkOut():
    open_new_window("out")
    
# Function to handle submit action and store user details
def submit():
    global name_value, email_value
    name_value = name_entry.get()
    email_value = email_entry.get()
    open_new_window("create")
    
def delete():
    open_new_window("delete")

# Set up the main window
base = Tk()
base.geometry("800x480")
base.eval('tk::PlaceWindow . center')  # Center the window
base.title("Swipe In System")

# Set a gradient background color
base.config(bg="#F5F5F5")

# Create a container (frame) for all UI elements with rounded corners
canvas = tk.Frame(base, bg='white', bd=5, relief='ridge')
canvas.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.85, relheight=0.8)
canvas.grid_columnconfigure(0, weight=1)  # Ensure layout flexibility
canvas.grid_columnconfigure(1, weight=1)


    
#check in or out for registered users
    
check_label = Label(canvas, text="Registered Users", width=20, font=("Helvetica", 22, "bold"), bg='#FFFFFF', fg='#333333')
check_label.grid(row=1, column=0, pady=10, padx=30)

checkInBtn = Button(master=canvas, text="Check In", command=checkIn, font=("Helvetica", 18, "bold"), bg='#D6EAF8', fg='black', relief=FLAT, bd=0,activebackground='#FCF3CF' )
checkInBtn.grid(row=3, column=0, pady=10, padx=30, columnspan=1)

checkOutBtn = Button(master=canvas, text="Check Out", command=checkOut, font=("Helvetica", 18, "bold"), bg='#D6EAF8', fg='black', relief=FLAT, bd=0, activebackground='#FCF3CF' )
checkOutBtn.grid(row=4, column=0, pady=10, padx=30, columnspan=1)

# Account creation section
createAccountLabel = Label(canvas, text="Create Account", width=20, font=("Helvetica", 22, "bold"), bg='#FFFFFF', fg='#333333')
createAccountLabel.grid(row=1, column=1, pady=10, padx=30)

# Name input field 
name_label = Label(canvas, text="Enter Name", width=10, font=("Helvetica", 16), bg='#FFFFFF', fg='#555555')
name_label.grid(row=2, column=1, pady=10, padx=30)
name_entry = Entry(canvas, width=20, font=("Helvetica", 16), relief=SOLID, bd=2, fg='#333333', highlightthickness=2, highlightcolor='#FF8C8C')
name_entry.grid(row=3, column=1, pady=10, padx=30)

# Email input field 
email_label = Label(canvas, text="Enter Email", width=10, font=("Helvetica", 16), bg='#FFFFFF', fg='#555555')
email_label.grid(row=4, column=1, pady=10, padx=30)
email_entry = Entry(canvas, width=20, font=("Helvetica", 16), relief=SOLID, bd=2, fg='#333333', highlightthickness=2, highlightcolor='#FF8C8C')
email_entry.grid(row=5, column=1, pady=10, padx=30)



submitBtn = Button(master=canvas, text="SUBMIT", command=submit, font=("Helvetica", 16, "bold"), bg='#D6EAF8', fg='black', relief=FLAT, bd=0, activebackground='#FCF3CF' )
submitBtn.grid(row=6, column=1, pady=20, padx=40, ipadx=5, ipady=5)

deleteBtn = Button(master=canvas, text="Delete Account", command=delete, font=("Helvetica", 16, "bold"), bg='#F9E79F', fg='black', relief=FLAT, bd=0, activebackground='#FAB8AF' )
deleteBtn.grid(row=6, column=0, pady=20, padx=40, ipadx=5, ipady=5)

# Start the Tkinter event loop
base.mainloop()
