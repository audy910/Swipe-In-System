import smtplib
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
        

