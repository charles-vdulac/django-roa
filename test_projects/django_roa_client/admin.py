from django.contrib import admin
from models import RemotePage, RemotePageWithManyFields

class RemotePageAdmin(admin.ModelAdmin):
    list_per_page = 2


class RemotePageWithManyFieldsAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'boolean_field', 'char_field')
    list_filter = ('boolean_field',)

admin.site.register(RemotePage, RemotePageAdmin)
admin.site.register(RemotePageWithManyFields, RemotePageWithManyFieldsAdmin)
