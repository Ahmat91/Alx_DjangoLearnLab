
from .models import Notification
from django.contrib.contenttypes.models import ContentType

def create_notification(recipient, actor, verb, target):
    """Creates a notification instance for a given action."""
    
    # Prevent notifying a user for an action they performed on themselves (e.g., self-like)
    if recipient == actor:
        return
        
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        target_content_type=ContentType.objects.get_for_model(target),
        target_object_id=target.pk,
        target=target
    )