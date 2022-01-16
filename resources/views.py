import csv

from django.views.generic import (
    View, TemplateView, ListView, DetailView, UpdateView, DeleteView, CreateView
)
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic.base import ContextMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Lower

from .forms import CreateEntryForm, GlossaryUploadForm
from .models import Entry, Glossary, GlossaryUploadFile


class ResourceListMixin(ContextMixin, View):
    '''
    Class used to populate the resources dropdown list.
    Implemented as a base class to avoid repeating in each view.
    '''
    def get_context_data(self, **kwargs):
        resources = Glossary.objects.all().order_by(Lower('title'))
        context = super().get_context_data(**kwargs)
        context['resources'] = resources
        return context


class HomePageView(LoginRequiredMixin, ResourceListMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        # Get the last ten entries added
        recent_terms = Entry.objects.all().order_by('-id')[:10]

        context = super(HomePageView, self).get_context_data(**kwargs)
        context.update({
            'recent_terms': recent_terms
        })
        return context


class SearchResultsView(LoginRequiredMixin, ResourceListMixin, ListView):
    model = Entry
    template_name = 'search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('query').strip()
        resource = self.request.GET.get('resource')
        if resource == 'All resources':
            queryset = Entry.objects.filter(
                Q(source__icontains=query) | Q(target__icontains=query)
            )
        else:
            queryset = Entry.objects.filter(
                Q(glossary__title=resource),
                Q(source__icontains=query) | Q(target__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        query = self.request.GET.get('query').strip()
        target_resource = self.request.GET.get('resource')
        hits = self.get_queryset().count()
        context.update({
            'target_resource': target_resource,
            'hits': hits,
            'query': query
        })
        return context


class EntryDetailView(LoginRequiredMixin, ResourceListMixin, DetailView):
    model = Entry
    template_name = 'entry_detail.html'


class EntryCreateView(LoginRequiredMixin, ResourceListMixin, CreateView):
    model = Entry
    form_class = CreateEntryForm
    template_name = 'entry_create.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class EntryUpdateView(LoginRequiredMixin, ResourceListMixin, UpdateView):
    model = Entry
    template_name = 'entry_update.html'
    fields = ('source', 'target', 'glossary', 'notes')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class EntryDeleteView(LoginRequiredMixin, ResourceListMixin, DeleteView):
    model = Entry
    template_name = 'entry_delete.html'
    success_url = reverse_lazy('home')


class GlossaryUploadView(LoginRequiredMixin, ResourceListMixin, View):
    form_class = GlossaryUploadForm
    template_name = 'glossary_upload.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            glossary_file = GlossaryUploadFile.objects.latest("uploaded_on")
            new_entries = []  # list for new Entry objects created from the uploaded file content

            with open(glossary_file.file_name.path, "r") as f:

                reader = csv.reader(f, delimiter='\t')

                # Create new Glossary object and save to DB
                new_glossary = Glossary(title=glossary_file.glossary_name)
                new_glossary.save()

                # Loop for creating new Entry objects from content of uploaded file
                for row in reader:

                    # Each row should contain 2 or 3 elements, otherwise ignored
                    if (len(row) == 2) or (len(row) == 3):

                        # Handling for optional notes item
                        if len(row) == 3:
                            notes = row[2]
                        else:
                            notes = ''

                        # Create Entry object and append to list
                        new_entry = Entry(
                            source=row[0],
                            target=row[1],
                            glossary=new_glossary,
                            notes=notes,
                            created_on=timezone.now(),
                            created_by=request.user,
                            updated_on=timezone.now(),
                            updated_by=request.user,
                        )

                        new_entries.append(new_entry)

            # Add all Entry objects to the database
            Entry.objects.bulk_create(new_entries)

            # Delete the uploaded text file after DB entries have been created
            glossary_file.delete()

            return redirect("home")

        return render(request, self.template_name, {'form': form})
