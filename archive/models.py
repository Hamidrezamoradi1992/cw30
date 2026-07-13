import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, Case, When, IntegerField
from django.utils.translation import gettext_lazy as _

from archive.messages import Messages

# Create your models here.

User = get_user_model()


class Category(models.Model):
    owner_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='archive_category',
        verbose_name=_('Owner User')
    )
    name = models.CharField(max_length=120, verbose_name=_('Name'))

    class Meta:
        ordering = ['id']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name


class File(models.Model):
    ALLOWED_FORMATS = [
        # Documents
        'pdf', 'doc', 'docx', 'odt',
        # Spreadsheets
        'xls', 'xlsx', 'ods',
        # Presentations
        'ppt', 'pptx', 'odp',
        # Text
        'txt',
        # Images
        'jpg', 'jpeg', 'png',
        # Archives
        'zip', 'rar', '7z'
    ]
    owner_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='file_owner_user',
        verbose_name=_('Owner User')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='archive_file_category',
        verbose_name=_('Category')
    )
    owner = models.ForeignKey(User,
                              on_delete=models.SET_NULL,
                              null=True,
                              related_name="file_owner",
                              verbose_name=_('Owner'))
    name = models.CharField(max_length=1024,
                            blank=True,
                            null=True,
                            verbose_name=_('File Name'))
    label = models.JSONField(verbose_name=_('Label'))
    file = models.FileField(upload_to='archive/',
                            null=False,
                            blank=False,
                            verbose_name=_('File'))
    size = models.IntegerField(null=True,
                               blank=True,
                               verbose_name=_('Size'))
    uploaded_at = models.DateTimeField(auto_now_add=True,
                                       verbose_name=_('Uploaded At'))
    file_format = models.CharField(max_length=50,
                                   blank=True,
                                   verbose_name=_('File Format'))

    def clean(self):
        """
        Validation for file format.
        """
        if self.file:
            ext = os.path.splitext(self.file.name)[1][1:].lower()  # get extension without dot
            if ext not in self.ALLOWED_FORMATS:
                raise ValidationError(
                    f"{Messages.file_unsupported_formats}: '{ext}'. "
                    f"{Messages.file_allowed_formats}: {', '.join(self.ALLOWED_FORMATS)}")

    def save(self, *args, **kwargs):
        """
        Override save method to set file type, name, size, and check storage limits.
        """
        if self.file:
            self.clean()
            # Calculate total used storage and check against max storage
            total_used = self.total_available(owner_user=self.owner_user)
            storage = settings.MAX_STORAGE * 1_000_000_000  # Convert GB to bytes
            max_free = storage - total_used
            file_size = self.file.size
            # Check if there is enough storage
            if max_free < file_size:
                raise ValidationError(
                    f"Insufficient storage space. Available: {max_free} bytes, Required: {file_size} bytes."
                )

            file_name = self.file.name.split('.')
            self.file_format = file_name[-1].lower()
            self.name = file_name[0].lower()
            self.size = file_size

        super().save(*args, **kwargs)

    def total_available(self, owner_user: object):
        """
        Calculate the total size of all files.
        """
        total = File.objects.all().aggregate(total_size=Sum('size'))['total_size'] or 0
        return total

    def get_storage_details(self, owner_user: object) -> dict:
        """
        Calculate storage details (total, word, excel, pdf, free) in one query.
        """
        result = File.objects.all().aggregate(
            total_size=Sum('size'),
            word_size=Sum(
                Case(
                    When(file_format__in=['doc', 'docx'], then='size'),
                    output_field=IntegerField(),
                    default=0
                )
            ),
            excel_size=Sum(
                Case(
                    When(file_format__in=['xls', 'xlsx'], then='size'),
                    output_field=IntegerField(),
                    default=0
                )
            ),
            pdf_size=Sum(
                Case(
                    When(file_format__in=['pdf'], then='size'),
                    output_field=IntegerField(),
                    default=0
                )
            )
        )
        total_size = result['total_size'] or 0
        storage = settings.MAX_STORAGE * 1_000_000_000
        return {
            'total_available': total_size,
            'word_available': result['word_size'] or 0,
            'excel_available': result['excel_size'] or 0,
            'pdf_available': result['pdf_size'] or 0,
            'free_storage': storage - total_size
        }

    def __str__(self):
        """
        String representation of the file.
        """
        return f"{self.name or self.file.name} (Key: {self.id})"

    class Meta:
        ordering = ['uploaded_at']
        verbose_name = _('File')
        verbose_name_plural = _('Files')


class Action(models.TextChoices):
    DELETE = "delete", _("delete")
    DOWNLOAD = "download", _("download")


class FileDownloadLog(models.Model):
    owner_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='download_logs_owner_user',
        verbose_name=_('Owner User')
    )
    file = models.CharField(max_length=180)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name="download_logs_user_id",
                                verbose_name=_('User ID'))
    downloaded_at = models.DateTimeField(auto_now_add=True,
                                         verbose_name=_('Downloaded At'))
    action = models.CharField(
        help_text=_("type field"),
        max_length=40,
        choices=Action.choices,
        default=Action.DOWNLOAD,
        verbose_name=_('Action')
    )

    class Meta:
        ordering = ['id']
        verbose_name = _('File Download Log')
        verbose_name_plural = _('File Download Logs')

    def __str__(self):
        return f"Download of {self.file} by {self.user_id} at {self.downloaded_at}"
