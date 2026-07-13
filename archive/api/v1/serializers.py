import uuid

from django.contrib.auth import get_user_model
from rest_framework import serializers

from archive.api.v1.exceptions import CustomValidationException
from archive.messages import Messages
from archive.models import Category, File, FileDownloadLog, Action

User = get_user_model()

class BaseUserInfoSerializer(serializers.ModelSerializer):
    """User Info serializer"""
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            # "id",
            "fullname",
            # "avatar",
        ]

    def get_fullname(self, obj) -> str:
        return obj.full_name


class CategorySetSerializers(serializers.ModelSerializer):
    """Serializer for creating or updating a category."""
    name = serializers.CharField(
        required=True,
        error_messages={'required': Messages.name_missing}
    )

    class Meta:
        model = Category
        fields = ("name",)

    def save(self, **kwargs):
        """Save category with user validation, ensuring unique name per owner."""
        request = self.context["request"]
        user = request.user
        name = self.validated_data.get("name")

        category = Category.objects.filter(name=name).exists()
        if category:
            raise CustomValidationException({"detail": Messages.category_already_exists})
        kwargs["owner_user"] = user
        return super().save(**kwargs)


class CategorySetResponseSerializer(serializers.Serializer):
    """Serializer for the response of category set."""
    message = serializers.CharField(read_only=True)

    class Meta:
        fields = ['message']


class CategoryListResponseSerializers(serializers.ModelSerializer):
    """Serializer for listing categories with name and ID."""

    class Meta:
        model = Category
        fields = ("name", "id")


class CategoryDestroySerializer(serializers.ModelSerializer):
    """Serializer for archiving a category by ID."""
    id = serializers.UUIDField()

    class Meta:
        model = Category
        fields = ["id"]

    def archive_or_delete(self, user) -> dict:
        """Archive a category for the given user, returning success message and ID."""
        category_id = self.validated_data.get("id")
        category = Category.objects.filter(
            id=category_id
        ).first()
        if not category:
            raise CustomValidationException({"detail": Messages.category_invalid})

        category.is_archived = True
        category.delete()

        return {
            "message": "Category archived successfully",
            "data_base_farm": {"id": category.id}
        }


class CategoryDestroyResponseSerializer(serializers.Serializer):
    """Serializer for the response of file category destroy."""
    message = serializers.CharField(read_only=True)
    data = serializers.DictField(read_only=True)

    class Meta:
        fields = ['message', 'data_base_farm']


class FileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and saving a file to the media folder."""
    file = serializers.FileField(required=True)
    category = serializers.CharField(required=True)
    label = serializers.JSONField(required=True)

    class Meta:
        model = File
        fields = [
            'id', 'owner_user', 'category', 'owner', 'name',
            'label', 'file', 'size', 'uploaded_at', 'file_format'
        ]
        read_only_fields = ['id', 'owner_user', 'owner', 'name',
                            'size', 'uploaded_at', 'file_format']

    def validate(self, attrs):
        """Validate that the label field contains a 'label' key."""
        label = attrs.get("label")
        if "label" not in label:
            raise CustomValidationException({"detail": Messages.label_missing})
        return super().validate(attrs)

    def save(self, **kwargs):
        """Save file with validated category and user, assigning owner fields."""
        request = self.context["request"]
        user = request.user

        category_name = self.validated_data.get("category")
        try:
            category_object = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            raise CustomValidationException({"detail": Messages.category_invalid})

        self.validated_data["category"] = category_object
        self.validated_data["owner_user"] = user
        self.validated_data["owner"] = user
        return super().save(**kwargs)


class FileResponseSerializers(serializers.ModelSerializer):
    """Serializer for file response with owner details."""
    owner = BaseUserInfoSerializer()
    category = CategoryListResponseSerializers()

    class Meta:
        model = File
        fields = ("id", "name", "owner", "category", "size", "label", "file_format", "uploaded_at")


class FileDownloadSerializer(serializers.Serializer):
    """Serializer for logging file downloads and returning file metadata."""
    id = serializers.UUIDField(required=False)
    file_url = serializers.URLField(read_only=True)

    class Meta:
        fields = ["name", "file_url"]

    def file_download_log(self, user, file_id) -> dict:
        """Log file download and return file name and URL."""
        try:
            id = uuid.UUID(str(file_id))
            file_obj = File.objects.filter(id=id).first()
            if not file_obj:
                raise CustomValidationException({"detail": Messages.file_does_not_exists})

            FileDownloadLog.objects.create(
                owner_user=user,
                user_id=user,
                file=f"name:{file_obj.name} / path:{file_obj.file.url}",
                action=Action.DOWNLOAD
            )

            file_url = file_obj.file.url
            return {
                "name": file_obj.name,
                "file_url": file_url
            }
        except Exception as e:
            raise CustomValidationException({"detail": f"{e}"})


class FileDownloadResponseSerializer(serializers.Serializer):
    """Serializer for the response of file download."""
    name = serializers.CharField(read_only=True)
    file_url = serializers.URLField(read_only=True)

    class Meta:
        fields = ['name', 'file_url']


class FileDestroySerializer(serializers.Serializer):
    """Serializer for logging and deleting a file by ID."""
    id = serializers.UUIDField(read_only=False, required=True)

    def file_destroy_log(self, user, file_id) -> dict:
        """Log file deletion and delete the file, returning success message."""
        try:
            id = uuid.UUID(str(file_id))
            file_obj = File.objects.filter(id=id).first()
            if not file_obj:
                raise CustomValidationException({"detail": Messages.file_does_not_exists})

            FileDownloadLog.objects.create(
                owner_user=user,
                user_id=user,
                file=f"name:{file_obj.name} / path:{file_obj.file.url}",
                action=Action.DELETE
            )
            file_name = file_obj.name
            file_obj.delete()
            return {
                "message": "File archived successfully",
                "data_base_farm": {'name': file_name,
                                   "id": file_id,
                                   }
            }
        except Exception as e:
            raise CustomValidationException({"detail": f"{e}"})


class FileDestroyResponseSerializer(serializers.Serializer):
    """Serializer for the response of file deletion."""
    message = serializers.CharField(read_only=True)
    data = serializers.DictField(read_only=True)

    class Meta:
        fields = ['message', 'data_base_farm']


class WordSerializers(serializers.Serializer):
    total = serializers.DecimalField(max_digits=8, decimal_places=6)
    color = serializers.CharField()

    class Meta:
        ref_name = "WordSerializers"


class ExcelSerializers(serializers.Serializer):
    total = serializers.DecimalField(max_digits=8, decimal_places=6)
    color = serializers.CharField()

    class Meta:
        ref_name = "ExcelSerializers"


class PdfSerializers(serializers.Serializer):
    total = serializers.DecimalField(max_digits=8, decimal_places=6)
    color = serializers.CharField()

    class Meta:
        ref_name = "PdfSerializers"


class OtherTypeSerializers(serializers.Serializer):
    total = serializers.DecimalField(max_digits=8, decimal_places=6)
    color = serializers.CharField()

    class Meta:
        ref_name = "OtherTypeSerializers"


class FileDietaileResponseSerializer(serializers.Serializer):
    total_storage = serializers.IntegerField()
    free_storage = serializers.DecimalField(max_digits=9, decimal_places=6)
    total_available = serializers.DecimalField(max_digits=8, decimal_places=6)
    word_available = WordSerializers()
    pdf_available = PdfSerializers()
    excel_available = ExcelSerializers()
    other_type = OtherTypeSerializers()
    # detail = serializers.CharField()


class PaginatedFileSerializer(serializers.Serializer):
    """Serializer for paginated File list response."""
    links = serializers.SerializerMethodField()
    total_items = serializers.IntegerField(source='paginator.count')
    total_pages = serializers.IntegerField(source='paginator.num_pages')
    results = FileCreateSerializer(many=True)

    def get_links(self, obj):
        """Generate links for next, previous, and current page."""
        page_obj = self.context.get('page_obj')
        page_number = self.context.get('page_number')
        return {
            'next': page_obj.get_next_link() if page_obj else None,
            'previous': page_obj.get_previous_link() if page_obj else None,
            'current': page_number,
        }
