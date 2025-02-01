from models.user import User
from models.gas_request import GasRequest
from app import db
import smtplib
from twilio.rest import Client

# Twilio Configuration for SMS
TWILIO_SID = "your_twilio_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "+1234567890"

# Email Configuration
EMAIL_HOST = "smtp.example.com"
EMAIL_PORT = 587
EMAIL_USERNAME = "your_email@example.com"
EMAIL_PASSWORD = "your_email_password"


def send_sms(phone_number, message):
    """Send an SMS notification using Twilio."""
    if not phone_number:
        print("No phone number provided. Skipping SMS.")
        return

    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"SMS sent to {phone_number}")
    except Exception as e:
        print(f"Error sending SMS: {e}")


def send_email(to_email, subject, body):
    """Send an email notification."""
    if not to_email:
        print("No email provided. Skipping email notification.")
        return

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(EMAIL_USERNAME, to_email, message)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")


def notify_consumer(user_id, message):
    """Send a notification (SMS & Email) to the consumer."""
    user = User.query.get(user_id)

    if not user:
        print(f"User {user_id} not found. Cannot send notification.")
        return

    # Send SMS if phone number is available
    send_sms(user.phone, message)

    # Send Email if email is available
    send_email(user.email, "Gas Request Update", message)

    print(f"Notification sent to user {user_id}: {message}")
