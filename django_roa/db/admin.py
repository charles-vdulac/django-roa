from django.contrib.admin.options import ModelAdmin as DjangoModelAdmin
from django.contrib.admin.options import StackedInline as DjangoStackedInline, \
                                         TabularInline as DjangoTabularInline

class ROAModelAdmin(DjangoModelAdmin):
    pass

class ROAStackedInline(DjangoStackedInline):
    pass

class ROATabularInline(DjangoTabularInline):
    pass
