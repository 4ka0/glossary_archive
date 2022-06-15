from django.urls import path
from .views import (
    HomePageView,
    SearchResultsView,
    EntryCreateView,
    EntryDetailView,
    EntryUpdateView,
    EntryDeleteView,
    GlossaryUploadView,
    GlossaryExportView,
    GlossaryDetailView,
    GlossaryCreateView,
    GlossaryDeleteView,
    GlossaryAddEntryView,
    GlossaryAllEntryView,
    GlossaryUpdateView,
    TranslationDetailView,
    TranslationUpdateView,
    TranslationDeleteView,
    TranslationShowAllView,
)


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('search/', SearchResultsView.as_view(), name='search_results'),

    path('entry/new/', EntryCreateView.as_view(), name='entry_create'),
    path('entry/<int:pk>/', EntryDetailView.as_view(), name='entry_detail'),
    path('entry/<int:pk>/edit/', EntryUpdateView.as_view(), name='entry_update'),
    path('entry/<int:pk>/delete/', EntryDeleteView.as_view(), name='entry_delete'),

    path('glossary/upload/', GlossaryUploadView.as_view(), name='glossary_upload'),
    path('glossary/export/', GlossaryExportView.as_view(), name='glossary_export'),
    path('glossary/<int:pk>/', GlossaryDetailView.as_view(), name='glossary_detail'),
    path('glossary/new/', GlossaryCreateView.as_view(), name='glossary_create'),
    path('glossary/<int:pk>/delete/', GlossaryDeleteView.as_view(), name='glossary_delete'),
    path('glossary/<int:glossary>/add/', GlossaryAddEntryView.as_view(), name='glossary_add_entry'),
    path('glossary/<int:pk>/all/', GlossaryAllEntryView.as_view(), name='glossary_all_entries'),
    path('glossary/<int:pk>/edit/', GlossaryUpdateView.as_view(), name='glossary_update'),

    path('translation/<int:pk>/', TranslationDetailView.as_view(), name='translation_detail'),
    path('translation/<int:pk>/edit/', TranslationUpdateView.as_view(), name='translation_update'),
    path('translation/<int:pk>/delete/', TranslationDeleteView.as_view(), name='translation_delete'),
    path('translation/<int:pk>/all/', TranslationShowAllView.as_view(), name='translation_show'),
]
