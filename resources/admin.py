from django.contrib import admin

from .models import Entry, CsvUploadFile


class EntryAdmin(admin.ModelAdmin):
    list_display = ('source', 'target', 'resource')


admin.site.register(Entry, EntryAdmin)
admin.site.register(CsvUploadFile)
