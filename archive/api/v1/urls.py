from django.urls import path

from archive.api.v1 import views

app_name = "api-v1"

urlpatterns = [
    path(
        "add-category",
        views.CategoryViewSet.as_view({"post": "add_category_archive"}),
        name="add-category-archive",
    ),
    path(
        "list-category",
        views.CategoryViewSet.as_view({"get": "list_category_archive"}),
        name="list-category-archive",
    ),
    path(
        "destroy-category",
        views.CategoryViewSet.as_view({"delete": "destroy_category_archive"}),
        name="destroy-category-archive",
    ),
    # file archive
    path(
        "create-file",
        views.FileViewSet.as_view({"post": "add_file_archive"}),
        name="add-file-archive",
    ),

    path(
        "download-file",
        views.FileViewSet.as_view({"get": "download_file_archive"}),
        name="download-file-archive",
    ),

    path(
        "destroy-file",
        views.FileViewSet.as_view({"delete": "destroy_file_archive"}),
        name="destroy-file-archive",
    ),

    # file list
    # path(
    #     "list-file",
    #     views.FileViewSet.as_view({"get": "list_file_archive"}),
    #     name="list-file-archive",
    # ),
    path(
        "file-list",
        views.ListFileArchiveViewSet.as_view({"get": "list"}),
        name="destroy-file-archive",
    ),

    path(
        "detaile-storage",
        views.DetailerStorageViewSet.as_view({"get": "detail_storage"}),
        name="file-detail_storage",
    ),

    # path('bulk-create/', views.BulkCreateFromExcelView.as_view()),
]
