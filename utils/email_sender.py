import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv() 

def send_news_digest(subject: str, body_html: str):
    """Sends the news digest email using SMTP credentials from .env."""
    
    # Retrieve credentials securely
    sender = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    recipient = os.getenv("RECIPIENT_EMAIL")

    if not all([sender, password, smtp_server, recipient]):
        print("ERROR: Missing one or more SMTP credentials in .env file. Email skipped.")
        return

    message = MIMEMultipart("alternative")
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    
    # Attach HTML content
    message.attach(MIMEText(body_html, "html"))
    
    try:
        # Connect to server and send
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server: 
            server.login(sender, password)
            server.sendmail(sender, recipient, message.as_string())
            print(f"SUCCESS: News digest sent to {recipient}")
    except Exception as e:
        print(f"ERROR sending email via SMTP: {e}")