from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.response import Response
from archive.api.v1.serializers import *




class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing category operations in the archive."""
    queryset = Category.objects.all()
    serializer_class = CategorySetSerializers

    def get_serializer_class(self):
        """Return the appropriate serializer based on the action."""
        serializer_dict = {
            "add_category_archive": CategorySetSerializers,
            "list_category_archive": CategoryListResponseSerializers,
            "destroy_category_archive": CategoryDestroySerializer,
        }
        return serializer_dict.get(self.action, self.serializer_class)

    # ───────────────────────────────────────────────
    # [POST] Add a new category to the archive
    # ───────────────────────────────────────────────
    @action(detail=False, methods=["post"], name="add_category_archive")

    def add_category_archive(self, request):
        """Create and save a new category for the authenticated user's organization."""
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {"message": Messages.information_correct}
        return Response(response, status=status.HTTP_200_OK)

    # ───────────────────────────────────────────────
    # [GET] List archived categories for current user's organization
    # ───────────────────────────────────────────────
    @action(detail=False, methods=["get"], name="list_category_archive")

    def list_category_archive(self, request):
        """Retrieve a list of categories filtered by user's organization."""
        user = request.user
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["delete"], name="destroy_category_archive")

    def destroy_category_archive(self, request):
        """Archive a category using ID from query parameters."""
        category_id = request.query_params.get("id")
        if not category_id:
            raise CustomValidationException({"detail": Messages.category_missing})
        serializer = self.get_serializer(data={"id": category_id})
        serializer.is_valid(raise_exception=True)
        result = serializer.archive_or_delete(user=request.user)
        return Response(result, status=status.HTTP_200_OK)


class FileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing file operations in the archive."""
    queryset = File.objects.all()
    serializer_class = FileCreateSerializer

    def get_serializer_class(self):
        """Return the appropriate serializer based on the action."""
        serializer_dict = {
            "add_file_archive": FileCreateSerializer,
            # "list_file_archive": FileResponseSerializers,
            "download_file_archive": FileDownloadSerializer,
            "destroy_file_archive": FileDestroySerializer,
        }
        return serializer_dict.get(self.action, self.serializer_class)


    @action(detail=False, methods=["post"], name="add_file_archive")

    def add_file_archive(self, request):
        """Upload and save a file to the media folder."""
        serializer = self.get_serializer(data=request.data, )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], name="download_file_archive")
    def download_file_archive(self, request):
        """Log file download and return file metadata with download URL."""
        serializer = self.get_serializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file_id = serializer.validated_data["id"]
        response_data = serializer.file_download_log(user=request.user, file_id=file_id)
        return Response(response_data, status=status.HTTP_200_OK)


    @action(detail=False, methods=["delete"], name="destroy_file_archive")
    def destroy_file_archive(self, request):
        """Delete a file and log the deletion action."""
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        file_id = serializer.validated_data["id"]
        response_data = serializer.file_destroy_log(user=request.user, file_id=file_id)
        return Response(data=response_data, status=status.HTTP_200_OK)


class ListFileArchiveViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileResponseSerializers

class DetailerStorageViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileDietaileResponseSerializer



    @action(detail=False, methods=["get"], name="detail_storage")
    def detail_storage(self, request, *args, **kwargs):
        file_instance = File()
        storage_details = file_instance.get_storage_details(owner_user=request.user)
        total_available = round(storage_details['total_available'] / 1_000_000_000, 6)
        free_storage = round(storage_details['free_storage'] / 1_000_000_000, 6)
        word_available = round(storage_details['word_available'] / 1_000_000_000, 6)
        excel_available = round(storage_details['excel_available'] / 1_000_000_000, 6)
        pdf_available = round(storage_details['pdf_available'] / 1_000_000_000, 6)
        other_type = round(total_available - (word_available + excel_available + pdf_available), 6)

        response_data = {
            'total_storage': settings.MAX_STORAGE,
            'free_storage': free_storage,
            'total_available': total_available,
            'word_available': {'total': word_available, 'color': '#9EE034'},
            'excel_available': {'total': excel_available, 'color': '#3479E0'},
            'pdf_available': {'total': pdf_available, 'color': '#E03434'},
            'other_type': {'total': other_type, 'color': "#E034D5"},
            # 'detail' :""
        }
        serializer = FileDietaileResponseSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
