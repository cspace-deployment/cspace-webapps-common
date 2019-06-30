from django.contrib import admin
from .models import AdditionalInfo

class AdditionalInfoAdmin(admin.ModelAdmin):

    def order(o):
        return o

    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'slug', 'order', 'contentType')

admin.site.register(AdditionalInfo, AdditionalInfoAdmin)