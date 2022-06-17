from django.contrib import admin

from .models import (
    Entry, Glossary, Translation, Segment, GlossaryUploadFile
)


class EntryAdmin(admin.ModelAdmin):
    list_display = ('source', 'target', 'glossary')


admin.site.register(Entry, EntryAdmin)
admin.site.register(Glossary)
admin.site.register(Translation)
admin.site.register(Segment)
admin.site.register(GlossaryUploadFile)
