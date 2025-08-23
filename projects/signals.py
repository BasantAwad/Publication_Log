# signals.py
import os

from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Publication
from .models import Message, Notification
from projects.AI.nlp_ba_model_1_with_adminreq_ import match_projects_and_papers

@receiver(post_save, sender=Publication)
def run_ai_matching(sender, instance, created, **kwargs):
    from django.conf import settings
    
    if os.environ.get("SEEDING") == "true":
        return  # Skip during seed
    
    # Skip if signals are disabled (for testing)
    if getattr(settings, 'SIGNALS_ENABLED', True) is False:
        return
    
    match_projects_and_papers(publication=instance)

@receiver(post_save, sender=Message)
def notify_unread_message(sender, instance, created, **kwargs):
    if created:
        # Create in-app notification
        Notification.objects.create(user=instance.recipient, message=instance)
        # Send email notification
        send_mail(
            'New Message Received',
            f'You have received a new message from {instance.sender.username}: "{instance.content[:100]}"',
            'noreply@yourdomain.com',
            [instance.recipient.email],
            fail_silently=True,
        )
