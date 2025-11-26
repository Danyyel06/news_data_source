import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_news_digest(subject: str, body_html: str):
    """Sends the news digest email using SMTP credentials from environment variables."""
    
    # Retrieve credentials from environment (no need for load_dotenv on Render)
    sender = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    recipient = os.getenv("RECIPIENT_EMAIL")

    # Debug logging
    print(f"Email config check:")
    print(f"  SMTP_USER: {'✓' if sender else '✗ MISSING'}")
    print(f"  SMTP_PASS: {'✓' if password else '✗ MISSING'}")
    print(f"  SMTP_SERVER: {smtp_server}")
    print(f"  SMTP_PORT: {smtp_port}")
    print(f"  RECIPIENT_EMAIL: {'✓' if recipient else '✗ MISSING'}")

    if not all([sender, password, smtp_server, recipient]):
        print("ERROR: Missing one or more SMTP credentials. Email skipped.")
        return

    message = MIMEMultipart("alternative")
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    
    # Attach HTML content
    message.attach(MIMEText(body_html, "html"))
    
    try:
        # Use SMTP with STARTTLS (not SMTP_SSL) for port 587
        print(f"Connecting to {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Enable TLS
            print("Logging in...")
            server.login(sender, password)
            print("Sending email...")
            server.sendmail(sender, recipient, message.as_string())
            print(f"✅ SUCCESS: News digest sent to {recipient}")
    except Exception as e:
        print(f"❌ ERROR sending email via SMTP: {e}")
        import traceback
        traceback.print_exc()