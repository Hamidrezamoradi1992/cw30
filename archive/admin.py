from django.contrib import admin
from archive import models
# Register your models here.
admin.site.register(models.File)
admin.site.register(models.FileDownloadLog)
admin.site.register(models.Category)