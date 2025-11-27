import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

def send_news_digest(subject: str, body_html: str):
    """Send email using SendGrid API with anti-spam optimizations"""
    
    api_key = os.getenv("SENDGRID_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL")
    sender_name = os.getenv("SENDER_NAME", "Financial News Alert")  # Add sender name
    recipient_email = os.getenv("RECIPIENT_EMAIL")
    
    print(f"📧 Email Configuration Check:")
    print(f"   SENDGRID_API_KEY: {'✓ Set' if api_key else '✗ MISSING'}")
    print(f"   SENDER_EMAIL: {sender_email if sender_email else '✗ MISSING'}")
    print(f"   SENDER_NAME: {sender_name}")
    print(f"   RECIPIENT_EMAIL: {recipient_email if recipient_email else '✗ MISSING'}")
    
    if not all([api_key, sender_email, recipient_email]):
        print("❌ ERROR: Missing SendGrid configuration")
        return
    
    try:
        print(f"📤 Preparing email...")
        print(f"   From: {sender_name} <{sender_email}>")
        print(f"   To: {recipient_email}")
        print(f"   Subject: {subject}")
        
        # Create plain text version (IMPORTANT for spam filters!)
        plain_text_body = create_plain_text_version(body_html)
        
        # Create the email message with improved headers
        message = Mail(
            from_email=Email(sender_email, sender_name),  # ← Add sender name
            to_emails=To(recipient_email),
            subject=subject,
            plain_text_content=Content("text/plain", plain_text_body),  # ← Add plain text
            html_content=Content("text/html", body_html)
        )
        
        # Add custom headers to avoid spam
        message.reply_to = Email(sender_email)
        
        # Send via SendGrid API
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        print(f"✅ SUCCESS: Email sent via SendGrid!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Message ID: {response.headers.get('X-Message-Id', 'N/A')}")
        
    except Exception as e:
        print(f"❌ ERROR sending email via SendGrid: {e}")
        import traceback
        traceback.print_exc()


def create_plain_text_version(html_content: str) -> str:
    """Create a plain text version of the HTML email (important for spam filters)"""
    # Simple HTML to text conversion
    import re
    
    # Remove HTML tags
    text = re.sub('<[^<]+?>', '', html_content)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Add a simple header
    plain_text = "REGULATORY NEWS DIGEST\n"
    plain_text += "=" * 50 + "\n\n"
    plain_text += text + "\n\n"
    plain_text += "=" * 50 + "\n"
    plain_text += "This is an automated news digest.\n"
    plain_text += "For best viewing, please enable HTML in your email client.\n"
    
    return plain_text