# Simple Mail Transfer Protocol
import smtplib, ssl
import datetime as datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dateutil.relativedelta import relativedelta
from django.conf import settings
from .TokenModels import UploadToken
from .models import Author
from .utils import is_valid_download_link
from .models import Publication


# Email config
SENDER = 'basantawad014@gmail.com'
EMAIL_PASSWORD = 'yuef auqt aohq razb'  # App password
RECEIVER_NAME = Publication.author
try:
    author_obj = Author.objects.get(name=RECEIVER_NAME)
    RECEIVER = author_obj.email
except Author.DoesNotExist:
    RECEIVER = None  # or some default email

context = ssl.create_default_context()

def generate_upload_link(receiver_email):
    try:
        user = Author.objects.get(email=receiver_email)
    except Author.DoesNotExist:
        print(f"⚠️ User not found for email: {receiver_email}")
        return "#"

    token = UploadToken.objects.create(user=user)
    upload_url = f"{settings.SITE_URL}/upload/{token.token}/"
    return upload_url

def personalize_template(template, title, end_date):
    html_body = template.replace("{{ researcher_name }}", RECEIVER.split('@')[0])
    html_body = html_body.replace("{{ project_title }}", title)
    html_body = html_body.replace("{{ project_end_date }}", end_date.strftime("%Y-%m-%d"))
    html_body = html_body.replace("{{ upload_link }}", generate_upload_link(RECEIVER))
    return html_body

def send_email(subject, html_body):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = SENDER
    msg['To'] = RECEIVER
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls(context=context)
            smtp.login(SENDER, EMAIL_PASSWORD)
            smtp.sendmail(SENDER, RECEIVER, msg.as_string())
            print(f"✅ Email sent to {RECEIVER}")
    except Exception as e:
        print(f"❌ Failed to send to {RECEIVER}: {e}")
    else:
        print(f"⏳ Not yet time to send to {RECEIVER}. Reminder scheduled for {reminder_date.date()}.")

# ========================
# LOGIC 1: 90% Reminder
# ========================
def send_90_percent_reminders(projects):
    with open('reminder.html', 'r', encoding='utf-8') as f:
        reminder = f.read()

    for project in projects:
        global RECEIVER, reminder_date  # Needed for outer variables used in `else` print
        RECEIVER, project_title, start_str, duration = project
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = start_date + relativedelta(months=duration)
        reminder_date = start_date + relativedelta(months=duration * 0.9)

        if datetime.now() >= reminder_date:
            with open('reminder.html', 'r', encoding='utf-8') as f:
                reminder = f.read()

            html_body = personalize_template(reminder, project_title, end_date)
            send_email(
                subject=f"⏰ Reminder: Upload Publication for '{project_title}'",
                html_body=html_body
            )

# ========================
# LOGIC 2: Final Reminder
# ========================
def send_final_reminders(projects):
    for project in projects:
        global RECEIVER
        RECEIVER, project_title, start_str, duration = project
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = start_date + relativedelta(months=duration)

        if datetime.now() >= end_date:
            with open('upload_reminder.html', 'r', encoding='utf-8') as f:
                reminder = f.read()

            html_body = personalize_template(reminder, project_title, end_date)
            send_email(
                subject=f"⚠️ Final Reminder: Project '{project_title}' Ended",
                html_body=html_body
            )

# ========================
# LOGIC 3: Invalid URL
# ========================
def notify_invalid_publication_url(pub, project_title, end_date):
    publication_url_valid = is_valid_download_link(pub.url)

    if publication_url_valid == False:
        with open('issue_email.html', 'r', encoding='utf-8') as f:
            issue = f.read()

        html_body = personalize_template(issue, project_title, end_date)
        send_email(
            subject=f"❗ Issue: Invalid Link for '{project_title}' Publication",
            html_body=html_body
        )
