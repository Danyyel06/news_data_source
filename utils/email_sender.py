import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_news_digest(subject: str, body_html: str):
    """Send email using SendGrid API"""
    
    api_key = os.getenv("SENDGRID_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL")
    recipient_email = os.getenv("RECIPIENT_EMAIL")
    
    print(f"📧 Email Configuration Check:")
    print(f"   SENDGRID_API_KEY: {'✓ Set' if api_key else '✗ MISSING'}")
    print(f"   SENDER_EMAIL: {sender_email if sender_email else '✗ MISSING'}")
    print(f"   RECIPIENT_EMAIL: {recipient_email if recipient_email else '✗ MISSING'}")
    
    if not all([api_key, sender_email, recipient_email]):
        print("❌ ERROR: Missing SendGrid configuration")
        return
    
    try:
        print(f"📤 Preparing email...")
        print(f"   From: {sender_email}")
        print(f"   To: {recipient_email}")
        print(f"   Subject: {subject}")
        
        # Create the email message
        message = Mail(
            from_email=sender_email,
            to_emails=recipient_email,
            subject=subject,
            html_content=body_html
        )
        
        # Send via SendGrid API
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        print(f"✅ SUCCESS: Email sent via SendGrid!")
        print(f"   Status Code: {response.status_code}")
        
    except Exception as e:
        print(f"❌ ERROR sending email via SendGrid: {e}")
        import traceback
        traceback.print_exc()