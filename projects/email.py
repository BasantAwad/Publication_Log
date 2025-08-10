# Simple Mail Transfer Protocol
import smtplib, ssl
import datetime as datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dateutil.relativedelta import relativedelta
from django.conf import settings
from .models import UploadToken
from .utils import is_valid_download_link
from .models import Publication
from .models import Author
from django.contrib.auth.models import User
import requests
import os


# Email config
SENDER = 'basantawad014@gmail.com'
EMAIL_PASSWORD = 'yuef auqt aohq razb'  # App password
RECEIVER_NAME = Publication.author
def get_author_by_name(name):
    return Author.objects.get(name=name)



context = ssl.create_default_context()

def generate_upload_link(request, receiver_email):
    try:
        user = User.objects.get(email=receiver_email)  # make sure this is a User, not Author
        token = UploadToken.objects.create(user=user)
        upload_url = request.build_absolute_uri(f"/upload/{token.token}/")
        return upload_url
    except User.DoesNotExist:
        return "No upload link available"


def personalize_template(request ,template, title, end_date):
    html_body = template.replace("{{ researcher_name }}", RECEIVER_NAME)
    html_body = html_body.replace("{{ project_title }}", title)
    html_body = html_body.replace("{{ project_end_date }}", end_date.strftime("%Y-%m-%d"))
    html_body = html_body.replace("{{ upload_link }}", generate_upload_link(request, RECEIVER))
    return html_body

def personalize_welcome_template(request ,template):
    receiver_name = str(RECEIVER_NAME)  # Ensure it's a string
    upload_link = generate_upload_link(request ,RECEIVER)
    
    html_body = template.replace("{{ researcher_name }}", receiver_name)
    html_body = html_body.replace("{{ upload_link }}", upload_link if upload_link else "No link available")  # Handle None case
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

# ========================
# LOGIC 1: 90% Reminder
# ========================
def send_90_percent_reminders(request ,projects):
    for project in projects:
        global RECEIVER, reminder_date  # Needed for outer variables used in `else` print
        RECEIVER, project_title, start_str, duration = project
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = start_date + relativedelta(months=duration)
        reminder_date = start_date + relativedelta(months=duration * 0.9)

        if datetime.now() >= reminder_date:
             try:
                template_path = os.path.join(settings.BASE_DIR, 'projects', 'templates', 'emails', 'reminder.html')
                with open(template_path, 'r', encoding='utf-8') as f:
                    reminder = f.read()
             except FileNotFoundError as e:
                print(f"❌ Reminder email template not found: {e}")
                continue

             html_body = personalize_template(request ,reminder, project_title, end_date)
             send_email(
                subject=f"⏰ Reminder: Upload Publication for '{project_title}'",
                html_body=html_body
               )

# ========================
# LOGIC 2: Final Reminder
# ========================
def send_final_reminders(request ,projects):
    for project in projects:
        global RECEIVER
        RECEIVER, project_title, start_str, duration = project
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = start_date + relativedelta(months=duration)

        if datetime.now() >= end_date:
            try:
                template_path = os.path.join(settings.BASE_DIR, 'projects', 'templates', 'emails', 'upload_reminder.html')
                with open(template_path, 'r', encoding='utf-8') as f:
                    reminder = f.read()
            except FileNotFoundError as e:
                print(f"❌ Upload reminder template not found: {e}")
                continue

            html_body = personalize_template(request ,reminder, project_title, end_date)
            send_email(
                subject=f"⚠️ Final Reminder: Project '{project_title}' Ended",
                html_body=html_body
            )

# ========================
# LOGIC 3: Invalid URL
# ========================
def notify_invalid_publication_url(request ,pub, project_title, end_date):
    publication_url_valid = is_valid_download_link(pub.url)

    if publication_url_valid == False:
        with open('emails/issue_email.html', 'r', encoding='utf-8') as f:
            issue = f.read()

        html_body = personalize_template(request ,issue, project_title, end_date)
        send_email(
            subject=f"❗ Issue: Invalid Link for '{project_title}' Publication",
            html_body=html_body
        )

# ========================
# LOGIC 4: Welcome Email
# ========================
def send_welcome_email(request ,user):
    global RECEIVER
    RECEIVER = user.email  # Set email for sending

 # Absolute path to the template file
    template_path = os.path.join(settings.BASE_DIR, 'projects', 'templates', 'emails', 'welcome_email.html')

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError as e:
        print(f"❌ Template file not found: {e}")
        return

    html_body = personalize_welcome_template(request ,template)

    send_email(
        subject="🎉 Welcome to the Publication Tracker!",
        html_body=html_body
    )

