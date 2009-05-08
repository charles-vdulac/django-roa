from django.contrib import admin
from django_roa import ModelAdmin
from models import RemotePage, RemotePageWithManyFields, RemotePageWithCustomSlug

class RemotePageAdmin(ModelAdmin):
    list_per_page = 2


class RemotePageWithManyFieldsAdmin(ModelAdmin):
    list_display = ('__unicode__', 'date_field', 'char_field')
    list_filter = ('date_field',)


class RemotePageWithCustomSlugAdmin(ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(RemotePage, RemotePageAdmin)
admin.site.register(RemotePageWithManyFields, RemotePageWithManyFieldsAdmin)
admin.site.register(RemotePageWithCustomSlug, RemotePageWithCustomSlugAdmin)
