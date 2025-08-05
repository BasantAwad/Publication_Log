from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Publication, CustomUser
from .AI.nlp_ba_model_1_with_adminreq_ import match_projects_and_papers

@receiver(post_save, sender=Publication)
def trigger_ai_on_publication_upload(sender, instance, created, **kwargs):
    if created:
        match_projects_and_papers(instance)

@receiver(post_save, sender=CustomUser)
def trigger_ai_on_user_registration(sender, instance, created, **kwargs):
    if created:
        match_projects_and_papers(user=instance)
