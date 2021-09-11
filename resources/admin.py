from django.contrib import admin

from .models import Entry, GlossaryUploadFile


class EntryAdmin(admin.ModelAdmin):
    list_display = ('source', 'target', 'resource')


admin.site.register(Entry, EntryAdmin)
admin.site.register(GlossaryUploadFile)
