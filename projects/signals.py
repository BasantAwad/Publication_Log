# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Publication
from .AI.nlp_ba_model_1_with_adminreq_ import match_projects_and_papers  # ✅ import your AI function

@receiver(post_save, sender=Publication)
def run_ai_matching(sender, instance, created, **kwargs):
    if created:  # ✅ only when a new Publication is created
        match_projects_and_papers(publication=instance)  # ✅ match this to your AI function signature
