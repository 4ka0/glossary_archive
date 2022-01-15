from django.urls import path
from .views import (
    HomePageView,
    SearchResultsView,
    EntryCreateView,
    EntryDetailView,
    EntryUpdateView,
    EntryDeleteView,
    GlossaryUploadView,
)


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('search/', SearchResultsView.as_view(), name='search_results'),

    path('entry/new/', EntryCreateView.as_view(), name='entry_create'),
    path('entry/<int:pk>/', EntryDetailView.as_view(), name='entry_detail'),
    path('entry/<int:pk>/edit/', EntryUpdateView.as_view(), name='entry_update'),
    path('entry/<int:pk>/delete/', EntryDeleteView.as_view(), name='entry_delete'),

    path('glossary/upload/', GlossaryUploadView.as_view(), name='glossary_upload'),
]
