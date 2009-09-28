from django.contrib import admin
from django_roa import ModelAdmin
from models import Tweet, User

class TweetAdmin(ModelAdmin):
    list_display = ('id', 'text', 'get_source_for_admin', 'get_user_link')

    def get_source_for_admin(self, item):
        return item.source
    get_source_for_admin.short_description = u'Source'
    get_source_for_admin.allow_tags = True

    def get_user_link(self, item):
        url = '../user/%s/' % (item.user.id)
        return '<a href="%s" title="">%s</a>' % (url, item.user)
    get_user_link.short_description = u'User'
    get_user_link.allow_tags = True

admin.site.register(Tweet, TweetAdmin)

class UserAdmin(ModelAdmin):
    list_display = ('screen_name',)

admin.site.register(User, UserAdmin)
