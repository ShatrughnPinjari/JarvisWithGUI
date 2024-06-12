import smtplib
import os
from dotenv import load_dotenv
import re

# Load environment variables from a .env file
load_dotenv(dotenv_path='..\\Data\\.env')

# Retrieve email credentials from environment variables
sender_id = os.getenv('EMAIL_ID')
password = os.getenv('PASSWORD')

def send_email(receiver_id, subject, body):
    # Create an SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    
    try:
        # Start TLS for security
        s.starttls()
        # Authenticate with the sender's email and password
        s.login(sender_id, password)
        
        # Construct the email message
        message = f"From: {sender_id}\nTo: {receiver_id}\nSubject: {subject}\n\n{body}"
        
        # Send the email
        s.sendmail(sender_id, receiver_id, message)
        
        print("Email sent successfully!")
        return True
    except smtplib.SMTPRecipientsRefused:
        print("INVALID EMAIL ADDRESS")
    except smtplib.SMTPException as e:
        print(f"Error: {str(e)}")
    finally:
        # Terminate the SMTP session
        s.quit()
    
    return False

def check_email(email):
    # Regular expression to validate email addresses
    verifier = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    return re.fullmatch(verifier, email) is not None


