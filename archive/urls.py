from django.urls import path, include

app_name = "archive"

urlpatterns = [
    # api based authentication
    path("api/v1/", include("archive.api.v1.urls"))
]
