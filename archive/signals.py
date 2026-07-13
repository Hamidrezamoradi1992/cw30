import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from archive.models import File
from utils.core.patern import BaseObserver


class DeleteFileObserver(BaseObserver):
    def update(self, sender, **kwargs):
        """
        When a File object is deleted, this Observer is called
        and deletes the actual file on disk.
        """
        instance = kwargs.get('instance')
        if instance and instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)


instance_observer = [
    DeleteFileObserver()
]


@receiver(post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    This function is called after a File object is deleted
    and calls DeleteFileObservers.
    """
    for observer in instance_observer:
        observer.update(sender=sender, instance=instance, **kwargs)
