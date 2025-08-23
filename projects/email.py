# Simple Mail Transfer Protocol
import datetime as datetime
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
import ssl

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone

from .models import UploadToken
from .models import Publication
from .models import Author
from .models import Message
from .utils import is_valid_download_link

# ========================
# EMAIL CONFIGURATION
# ========================
# SENDER: The sender's Gmail address.
SENDER = 'basantawad014@gmail.com'
# EMAIL_PASSWORD: App password generated for Gmail (never use your real password!).
EMAIL_PASSWORD = 'yuef auqt aohq razb'  # App password

# RECEIVER_NAME: Default receiver name. Used for template personalization. 
# (Note: This is set from Publication.primary_author, but is later overridden by logic per email.)
RECEIVER_NAME = "Test Author"

def get_author_by_name(name):
    """Helper to get an Author object by its name."""
    return Author.objects.get(name=name)

# SSL context for secure connection to Gmail's SMTP server
context = ssl.create_default_context()

def generate_upload_link(request, receiver_email):
    """
    Generate a secure upload link for a user to submit files.
    Used in email templates to provide personal upload URLs.
    """
    try:
        user = User.objects.get(email=receiver_email)  # make sure this is a User, not Author
        token = UploadToken.objects.create(user=user)
        upload_url = request.build_absolute_uri(f"/upload/{token.token}/")
        return upload_url
    except User.DoesNotExist:
        return "No upload link available"

def personalize_template(request, template, title, end_date):
    """
    Fill placeholders in email template for reminders or issues.
    - researcher_name, project_title, project_end_date, upload_link
    """
    html_body = template.replace("{{ researcher_name }}", RECEIVER_NAME)
    html_body = html_body.replace("{{ project_title }}", title)
    html_body = html_body.replace("{{ project_end_date }}", end_date.strftime("%Y-%m-%d"))
    html_body = html_body.replace("{{ upload_link }}", generate_upload_link(request, RECEIVER))
    return html_body

def personalize_welcome_template(request, template):
    """
    Fill placeholders for the welcome email template.
    Provides the new user with their upload link and name.
    """
    receiver_name = str(RECEIVER_NAME)  # Ensure it's a string
    upload_link = generate_upload_link(request, RECEIVER)
    html_body = template.replace("{{ researcher_name }}", receiver_name)
    html_body = html_body.replace("{{ upload_link }}", upload_link if upload_link else "No link available")  # Handle None case
    return html_body

def send_email(subject, html_body):
    """
    Send an HTML email using Gmail's SMTP server.
    - subject: Email subject line.
    - html_body: The HTML content of the email.
    """
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
def send_90_percent_reminders(request, projects):
    """
    For each project, if 90% of its duration has passed, send a reminder email to upload a publication.
    - Reads the reminder email template and personalizes it.
    - Only sends the email if the current date >= reminder date.
    """
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

            html_body = personalize_template(request, reminder, project_title, end_date)
            send_email(
                subject=f"⏰ Reminder: Upload Publication for '{project_title}'",
                html_body=html_body
            )

# ========================
# LOGIC 2: Final Reminder
# ========================
def send_final_reminders(request, projects):
    """
    For each project, if its end date has passed, send a final reminder to upload publications.
    - Reads the upload reminder email template and personalizes it.
    - Only sends the email if the current date >= end date.
    """
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

            html_body = personalize_template(request, reminder, project_title, end_date)
            send_email(
                subject=f"⚠️ Final Reminder: Project '{project_title}' Ended",
                html_body=html_body
            )

# ========================
# LOGIC 3: Invalid URL
# ========================
def notify_invalid_publication_url(request, pub, project_title, end_date):
    """
    If a publication's URL is invalid, send an issue notification email to the researcher.
    - Checks the validity using is_valid_download_link utility.
    - Uses the issue email template.
    """
    publication_url_valid = is_valid_download_link(pub.url)

    if publication_url_valid == False:
        with open('emails/issue_email.html', 'r', encoding='utf-8') as f:
            issue = f.read()

        html_body = personalize_template(request, issue, project_title, end_date)
        send_email(
            subject=f"❗ Issue: Invalid Link for '{project_title}' Publication",
            html_body=html_body
        )

# ========================
# LOGIC 4: Welcome Email
# ========================
def send_welcome_email(request, user):
    """
    Send a personalized welcome email to a newly registered user.
    - Reads the welcome email template and fills user-specific info.
    """
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

    html_body = personalize_welcome_template(request, template)

    send_email(
        subject="🎉 Welcome to the Publication Tracker!",
        html_body=html_body
    )




def send_unread_message_reminders():
    threshold = timezone.now() - timedelta(hours=2)
    unread = Message.objects.filter(is_read=False, sent_at__lt=threshold)
    for msg in unread:
        send_mail(
            'Reminder: Unread Message',
            f'You still have an unread message from {msg.sender.username}.',
            'noreply@yourdomain.com',
            [msg.recipient.email],
            fail_silently=True,
        )

# ========================
# MESSAGING EMAIL FUNCTIONS
# ========================

def send_message_notification_email(recipient, sender, message_content):
    """Send email notification for new messages"""
    try:
        from django.template.loader import render_to_string
        from django.utils import timezone
        
        subject = f"New message from {sender.username}"
        
        context = {
            'sender_name': sender.username,
            'message_preview': message_content[:200] + ('...' if len(message_content) > 200 else ''),
            'timestamp': timezone.now().strftime("%B %d, %Y at %I:%M %p"),
            'site_url': settings.SITE_URL,
        }
        
        html_content = render_to_string('emails/message_notification.html', context)
        
        send_email(subject, html_content, recipient.email)
        return True
    except Exception as e:
        print(f"Failed to send message notification email: {e}")
        return False

def send_message_request_email(recipient, sender, request_message):
    """Send email notification for message requests"""
    try:
        from django.template.loader import render_to_string
        from django.utils import timezone
        
        subject = f"Message request from {sender.username}"
        
        context = {
            'sender_name': sender.username,
            'request_message': request_message,
            'timestamp': timezone.now().strftime("%B %d, %Y at %I:%M %p"),
            'site_url': settings.SITE_URL,
            'request_id': '{{ request_id }}',  # This will be replaced by the view
        }
        
        html_content = render_to_string('emails/message_request.html', context)
        
        send_email(subject, html_content, recipient.email)
        return True
    except Exception as e:
        print(f"Failed to send message request email: {e}")
        return False

def send_request_approved_email(recipient, approver):
    """Send email notification when message request is approved"""
    try:
        from django.template.loader import render_to_string
        from django.utils import timezone
        
        subject = f"Message request approved by {approver.username}"
        
        context = {
            'approver_name': approver.username,
            'timestamp': timezone.now().strftime("%B %d, %Y at %I:%M %p"),
            'site_url': settings.SITE_URL,
        }
        
        html_content = render_to_string('emails/request_approved.html', context)
        
        send_email(subject, html_content, recipient.email)
        return True
    except Exception as e:
        print(f"Failed to send request approved email: {e}")
        return False

def send_group_message_notification_email(recipients, sender, group_name, message_content, group_id=None):
    """Send email notification for group messages"""
    try:
        from django.template.loader import render_to_string
        from django.utils import timezone
        
        subject = f"New group message in '{group_name}' from {sender.username}"
        
        context = {
            'sender_name': sender.username,
            'group_name': group_name,
            'group_id': group_id,
            'message_preview': message_content[:200] + ('...' if len(message_content) > 200 else ''),
            'timestamp': timezone.now().strftime("%B %d, %Y at %I:%M %p"),
            'site_url': settings.SITE_URL,
            'member_count': len(recipients) + 1,  # +1 for sender
        }
        
        html_content = render_to_string('emails/group_message_notification.html', context)
        
        for recipient in recipients:
            send_email(subject, html_content, recipient.email)
        return True
    except Exception as e:
        print(f"Failed to send group message notification email: {e}")
        return False

# ========================
# ENHANCED EMAIL FUNCTIONS
# ========================

def send_email(subject, html_body, recipient_email=None):
    """
    Enhanced email sending function that can handle both global and specific recipients
    """
    global RECEIVER
    
    if recipient_email:
        RECEIVER = recipient_email
    
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
            return True
    except Exception as e:
        print(f"❌ Failed to send to {RECEIVER}: {e}")
        return False

def send_publication_reminder_email(author, publication, project):
    """Send reminder email for publication upload"""
    try:
        from django.template.loader import render_to_string
        
        subject = f"Reminder: Upload Publication for '{project.title}'"
        
        context = {
            'author_name': author.name,
            'project_title': project.title,
            'project_domain': project.domain,
            'project_duration': project.duration,
            'project_start_date': project.start_date.strftime("%B %d, %Y") if project.start_date else "Not specified",
            'project_end_date': project.end_date.strftime("%B %d, %Y") if project.end_date else "Not specified",
            'project_id': project.id,
            'site_url': settings.SITE_URL,
            'deadline': project.end_date.strftime("%B %d, %Y") if project.end_date else None,
        }
        
        html_content = render_to_string('emails/publication_reminder.html', context)
        
        send_email(subject, html_content, author.email)
        return True
    except Exception as e:
        print(f"Failed to send publication reminder email: {e}")
        return False

def send_publication_upload_confirmation(author, publication, project):
    """Send confirmation email when publication is uploaded"""
    try:
        from django.template.loader import render_to_string
        from django.utils import timezone
        
        subject = f"Publication Uploaded: '{publication.title}'"
        
        # Get all authors for display
        authors_list = [author.name]
        if publication.collaborators.all():
            authors_list.extend([collab.name for collab in publication.collaborators.all()])
        authors_display = ", ".join(authors_list)
        
        context = {
            'author_name': author.name,
            'publication_title': publication.title,
            'publication_type': publication.type,
            'publication_year': publication.year,
            'publication_authors': authors_display,
            'publication_abstract': publication.abstract if publication.abstract else None,
            'publication_id': publication.id,
            'project_title': project.title,
            'timestamp': timezone.now().strftime("%B %d, %Y at %I:%M %p"),
            'site_url': settings.SITE_URL,
        }
        
        html_content = render_to_string('emails/publication_confirmation.html', context)
        
        send_email(subject, html_content, author.email)
        return True
    except Exception as e:
        print(f"Failed to send publication confirmation email: {e}")
        return False