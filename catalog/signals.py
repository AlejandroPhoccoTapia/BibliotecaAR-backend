"""Remove replaced/deleted media only after the owning DB transaction commits."""
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Book, Scene, StudentProfile


MEDIA_FIELDS = {
    Book: ('cover',),
    Scene: ('audio', 'glb_model', 'qr_image'),
    StudentProfile: ('photo',),
}


def schedule_cleanup(storage, name, using):
    if not name:
        return

    def delete_if_unreferenced():
        # All catalog media currently share the default storage. Preserve files
        # still referenced by another row, including across file fields.
        for model, fields in MEDIA_FIELDS.items():
            query = Q()
            for field in fields:
                query |= Q(**{field: name})
            if model.objects.using(using).filter(query).exists():
                return
        storage.delete(name)

    # A storage outage must be logged, not turn an already committed write into
    # an HTTP error that tempts the client to duplicate the operation.
    transaction.on_commit(delete_if_unreferenced, using=using, robust=True)


@receiver(pre_save)
def remember_previous_media(sender, instance, using, raw=False, **kwargs):
    if sender not in MEDIA_FIELDS or raw:
        return
    instance._previous_media = (
        sender.objects.using(using).filter(pk=instance.pk)
        .values(*MEDIA_FIELDS[sender]).first()
        if instance.pk else None
    ) or {}


@receiver(post_save)
def cleanup_replaced_media(sender, instance, using, raw=False, update_fields=None, **kwargs):
    if sender not in MEDIA_FIELDS or raw:
        return
    previous = getattr(instance, '_previous_media', {})
    for field in MEDIA_FIELDS[sender]:
        if update_fields is not None and field not in update_fields:
            continue
        current = getattr(instance, field)
        old_name = previous.get(field)
        if old_name and old_name != current.name:
            schedule_cleanup(current.storage, old_name, using)
    instance._previous_media = {}


@receiver(post_delete)
def cleanup_deleted_media(sender, instance, using, **kwargs):
    if sender not in MEDIA_FIELDS:
        return
    for field in MEDIA_FIELDS[sender]:
        file = getattr(instance, field)
        if file:
            schedule_cleanup(file.storage, file.name, using)
