from django.contrib import admin
from models import RemotePage

class RemotePageAdmin(admin.ModelAdmin):
    list_per_page = 2

admin.site.register(RemotePage, RemotePageAdmin)
