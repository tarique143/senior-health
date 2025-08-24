# backend/app/reminders.py

from datetime import datetime
from typing import List

import pytz
from fastapi_mail import FastMail, MessageSchema
from sqlalchemy.orm import Session

from app import models
from app.database import SessionLocal
from app.utils import conf  # Import the email config from utils.py

# Set the timezone to Indian Standard Time for accurate scheduling and display.
IST = pytz.timezone("Asia/Kolkata")


def create_email_body(user: models.User, meds_today: List[models.Medication]) -> str:
    """
    Generates a user-friendly HTML email body for the daily reminder.

    Args:
        user: The user object to whom the email is being sent.
        meds_today: A list of the user's active medications for the day.

    Returns:
        A string containing the complete HTML for the email body.
    """
    # Sort medications by their scheduled time for a clean, chronological list.
    sorted_meds = sorted(meds_today, key=lambda med: med.timing)

    med_list_html = ""
    if not sorted_meds:
        med_list_html = "<p>You have no medications scheduled for today. Have a great day!</p>"
    else:
        for med in sorted_meds:
            # Format the time into a 12-hour format (e.g., 08:30 AM).
            med_time = med.timing.strftime('%I:%M %p')
            med_list_html += f"""
            <div style="background-color: #f9f9f9; border-left: 5px solid #0068C9; padding: 10px 15px; margin-bottom: 10px; border-radius: 5px;">
                <p style="margin: 0; font-size: 18px; color: #333;"><strong>{med.name}</strong> ({med.dosage})</p>
                <p style="margin: 0; font-size: 16px; color: #0068C9;"><strong>Time: {med_time}</strong></p>
            </div>
            """

    # Get today's date in a readable format (e.g., "Monday, August 25, 2025").
    today_date_str = datetime.now(IST).strftime("%A, %B %d, %Y")

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <div style="text-align: center; border-bottom: 2px solid #eee; padding-bottom: 20px; margin-bottom: 20px;">
                <h1 style="color: #0068C9; margin: 0;">Health Companion</h1>
                <p style="font-size: 18px; color: #555; margin: 5px 0 0;">Your Daily Medication Reminder</p>
            </div>
            <h2 style="font-size: 20px;">Hello, {user.full_name}!</h2>
            <p style="font-size: 16px;">Here is your medication schedule for today, <strong>{today_date_str}</strong>:</p>
            {med_list_html}
            <div style="margin-top: 30px; text-align: center; font-size: 12px; color: #aaa;">
                <p>This is an automated reminder. Have a healthy and wonderful day!</p>
                <p>&copy; {datetime.now().year} Health Companion</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


async def send_daily_reminders():
    """
    The main job function executed by the scheduler.

    It queries the database for all users who have reminders enabled,
    fetches their active medications, and sends them a personalized
    reminder email.
    """
    # Create a new database session specifically for this background task.
    db: Session = SessionLocal()
    try:
        # Fetch all users who have the 'send_reminders' preference set to True.
        users_to_remind = db.query(models.User).filter(models.User.send_reminders == True).all()
        
        print(f"[{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}] Running daily reminder job. Found {len(users_to_remind)} users to remind.")

        for user in users_to_remind:
            # For each user, fetch only their medications that are marked as 'is_active'.
            meds_today = db.query(models.Medication).filter(
                models.Medication.owner_id == user.id,
                models.Medication.is_active == True
            ).all()

            # If the user has no active medications, skip sending an email.
            if not meds_today:
                print(f"Skipping reminder for {user.email} (no active medications).")
                continue

            html_body = create_email_body(user, meds_today)

            message = MessageSchema(
                subject=f"💊 Your Medication Schedule for Today - {datetime.now(IST).strftime('%B %d')}",
                recipients=[user.email],
                body=html_body,
                subtype="html"
            )

            fm = FastMail(conf)
            await fm.send_message(message)
            print(f"Successfully sent reminder to {user.email}")
            
    except Exception as e:
        print(f"An error occurred during the reminder job: {e}")
    finally:
        # It's crucial to close the database session in a background task.
        db.close()
