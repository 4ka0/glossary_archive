from django.contrib import admin

from .models import Entry, Glossary, GlossaryUploadFile


class EntryAdmin(admin.ModelAdmin):
    list_display = ('source', 'target', 'glossary',)


admin.site.register(Entry, EntryAdmin)
admin.site.register(Glossary)
admin.site.register(GlossaryUploadFile)
