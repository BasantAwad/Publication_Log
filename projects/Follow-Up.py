#Simple Mail Transfer Protocol
import smtplib, ssl
import datetime as datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dateutil.relativedelta import relativedelta
from django.conf import settings
from .models import UploadToken, User
from .utils import is_valid_download_link


# Email config
SENDER = 'basantawad014@gmail.com'
EMAIL_PASSWORD = 'yuef auqt aohq razb'  # App password
RECEIVER = 'roselover12332@gmail.com'



publication_url_valid =  is_valid_download_link(pub.url)

def generate_upload_link(receiver_email):
    try:
        user = User.objects.get(email=receiver_email)
    except User.DoesNotExist:
        print(f"⚠️ User not found for email: {receiver_email}")
        return "#"

    # Create or get a fresh token
    token = UploadToken.objects.create(user=user)
    upload_url = f"{settings.SITE_URL}/upload/{token.token}/"
    return upload_url

def personalize_template(template):
 # Personalize template
        html_body = template.replace("{{ researcher_name }}", RECEIVER.split('@')[0])
        html_body = html_body.replace("{{ project_title }}", title)
        html_body = html_body.replace("{{ project_end_date }}", end_date.strftime("%Y-%m-%d"))
        html_body = html_body.replace("{{ upload_link }}",generate_upload_link(RECEIVER))
        
        return html_body

context = ssl.create_default_context()

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



# Logic 1: 90% duration reminder
with open('reminder.html', 'r', encoding='utf-8') as f:
     reminder = f.read()

for project in projects:
    RECEIVER, project_title, start_str, duration = project
    start_date = datetime.strptime(start_str, "%Y-%m-%d")
    end_date = start_date + relativedelta(months=duration)
    reminder_date = start_date + relativedelta(months=duration * 0.9)

    # Reminder
    if datetime.now() >= reminder_date:
        with open('reminder.html', 'r', encoding='utf-8') as f:
            reminder = f.read()

        html_body = personalize_template(reminder, RECEIVER, project_title, end_date)
        send_email(
            subject=f"⏰ Reminder: Upload Publication for '{project_title}'",
            html_body=html_body,
            receiver=RECEIVER
        )

    # Final reminder
    if datetime.now() >= end_date:
        with open('upload_reminder.html', 'r', encoding='utf-8') as f:
            reminder = f.read()
        html_body = personalize_template(reminder, RECEIVER, project_title, end_date)
        send_email(
            subject=f"⚠️ Final Reminder: Project '{project_title}' Ended",
            html_body=html_body,
            receiver=RECEIVER
        )



# Logic 3: Publication link invalid
    if publication_url_valid==False:
        with open('issue_email.html', 'r', encoding='utf-8') as f:
         issue = f.read()
         html_body=personalize_template(issue)
        send_email(
        subject=f"❗ Issue: Invalid Link for '{project_title}' Publication",
        html_body= html_body
        )