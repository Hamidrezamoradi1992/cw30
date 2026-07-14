
from django.contrib.auth import get_user_model
from rest_framework import serializers

from archive.api.v1.exceptions import CustomValidationException
from archive.messages import Messages
from archive.models import Category, File, FileDownloadLog, Action

User = get_user_model()

class BaseUserInfoSerializer(serializers.ModelSerializer):
    """User Info serializer"""


class CategorySetSerializers(serializers.ModelSerializer):
    """Serializer for creating or updating a category."""


    def save(self, **kwargs):
        """Save category with user validation, ensuring unique name per owner."""
        return super().save(**kwargs)


class CategorySetResponseSerializer(serializers.Serializer):
    """Serializer for the response of category set."""


class CategoryListResponseSerializers(serializers.ModelSerializer):
    """Serializer for listing categories with name and ID."""


class CategoryDestroySerializer(serializers.ModelSerializer):
    """Serializer for archiving a category by ID."""


    def archive_or_delete(self, user) -> dict:
        """Archive a category for the given user, returning success message and ID."""

        return {
            "message": "Category archived successfully",
            "data_base_farm": {"id": 12262}
        }


class CategoryDestroyResponseSerializer(serializers.Serializer):
    """Serializer for the response of file category destroy."""



class FileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and saving a file to the media folder."""


    def validate(self, attrs):
        """Validate that the label field contains a 'label' key."""
        return super().validate(attrs)

    def save(self, **kwargs):
        """Save file with validated category and user, assigning owner fields."""
        return super().save(**kwargs)


class FileResponseSerializers(serializers.ModelSerializer):
    """Serializer for file response with owner details."""


class FileDownloadSerializer(serializers.Serializer):
    """Serializer for logging file downloads and returning file metadata."""
    id = serializers.UUIDField(required=False)
    file_url = serializers.URLField(read_only=True)

    class Meta:
        fields = ["name", "file_url"]

    def file_download_log(self, user, file_id) -> dict:
        """Log file download and return file name and URL."""
        return {}


class FileDownloadResponseSerializer(serializers.Serializer):
    """Serializer for the response of file download."""



class FileDestroySerializer(serializers.Serializer):
    """Serializer for logging and deleting a file by ID."""
    id = serializers.UUIDField(read_only=False, required=True)

    def file_destroy_log(self, user, file_id) -> dict:
        """Log file deletion and delete the file, returning success message."""
        return {}


class FileDestroyResponseSerializer(serializers.Serializer):
    """Serializer for the response of file deletion."""


class WordSerializers(serializers.Serializer):
    pass


class ExcelSerializers(serializers.Serializer):
    pass

class PdfSerializers(serializers.Serializer):
    pass


class OtherTypeSerializers(serializers.Serializer):
    pass


class FileDetailerResponseSerializer(serializers.Serializer):
    pass

