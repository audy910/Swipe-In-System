import smtplib
import os
from DatabaseFunctions import export_logs_to_text_file
from email.message import EmailMessage


def send_email(subject, body, to_email):
    EMAIL_ADDRESS = "swipeinservice@gmail.com"
    EMAIL_PASSWORD = "pjrm fxvr vifz ofvg" 

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
        

def send_logs(subject, body, to_email):
    EMAIL_ADDRESS = "swipeinservice@gmail.com"
    EMAIL_PASSWORD = "pjrm fxvr vifz ofvg" 

    # Export logs to file
    log_file = 'user_logs.txt'
    export_logs_to_text_file(log_file)

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(body)

    # Attach the log file
    try:
        with open(log_file, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(log_file)
            msg.add_attachment(file_data, maintype='text', subtype='plain', filename=file_name)
    except Exception as e:
        print(f"Failed to attach log file: {e}")
        return

    # Send the email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Email with logs sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


