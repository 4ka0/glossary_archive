import os
import csv
import shutil

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
from django.http import FileResponse

from .forms import (
    CreateEntryForm, GlossaryUploadForm, CreateGlossaryForm, AddEntryToGlossaryForm,
    GlossaryExportForm
)
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
        # Get all available glossaries
        glossaries = Glossary.objects.all().order_by('-id')

        # Get the last ten entries added
        recent_terms = Entry.objects.all().order_by('-id')[:10]
        total_entries = Entry.objects.count()

        context = super(HomePageView, self).get_context_data(**kwargs)
        context.update({
            'glossaries': glossaries,
            'recent_terms': recent_terms,
            'total_entries': total_entries,
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


class EntryDetailView(LoginRequiredMixin, DetailView):
    model = Entry
    template_name = 'entry_detail.html'


class EntryCreateView(LoginRequiredMixin, CreateView):
    model = Entry
    form_class = CreateEntryForm
    template_name = 'entry_create.html'

    def form_valid(self, form):
        obj = form.save(commit=False)

        obj.created_by = self.request.user
        obj.updated_by = self.request.user
        obj.save()

        # Sets user data on Glossary object if new Glossary is being created with the new Entry
        if obj.glossary.created_by is None and obj.glossary.updated_by is None:
            obj.glossary.created_by = self.request.user
            obj.glossary.updated_by = self.request.user
            obj.glossary.save()

        return HttpResponseRedirect(obj.get_absolute_url())


class EntryUpdateView(LoginRequiredMixin, UpdateView):
    model = Entry
    template_name = 'entry_update.html'
    fields = ('source', 'target', 'glossary', 'notes')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class EntryDeleteView(LoginRequiredMixin, DeleteView):
    model = Entry
    template_name = 'entry_delete.html'
    success_url = reverse_lazy('home')


class GlossaryUploadView(LoginRequiredMixin, View):
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
                new_glossary = Glossary(
                    title=glossary_file.glossary_name,
                    notes=glossary_file.glossary_notes,
                    created_by=request.user,
                    updated_by=request.user,
                )
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


class GlossaryDetailView(LoginRequiredMixin, DetailView):
    model = Glossary
    template_name = 'glossary_detail.html'

    def get_context_data(self, **kwargs):
        context = super(GlossaryDetailView, self).get_context_data(**kwargs)
        num_of_entries = context['glossary'].entries.all().count()
        context.update({
            'num_of_entries': num_of_entries,
        })
        return context


class GlossaryCreateView(LoginRequiredMixin, CreateView):
    model = Glossary
    form_class = CreateGlossaryForm
    template_name = 'glossary_create.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class GlossaryDeleteView(LoginRequiredMixin, DeleteView):
    model = Glossary
    template_name = 'glossary_delete.html'
    success_url = reverse_lazy('home')


class GlossaryAddEntryView(LoginRequiredMixin, CreateView):
    '''
    Class to add a new Entry object to an existing Glossary Object.
    Called from the Glossary detail page.
    Receives pk of Glossary object in question and sets this for the as entry.glossary field.
    '''
    model = Entry
    form_class = AddEntryToGlossaryForm
    template_name = 'glossary_add_entry.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.glossary = Glossary.objects.get(pk=self.kwargs['glossary'])
        obj.created_by = self.request.user
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class GlossaryUpdateView(LoginRequiredMixin, UpdateView):
    model = Glossary
    template_name = 'glossary_update.html'
    fields = ('title', 'notes')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class GlossaryAllEntryView(LoginRequiredMixin, DetailView):
    model = Glossary
    template_name = 'glossary_all.html'

    def get_context_data(self, **kwargs):
        context = super(GlossaryAllEntryView, self).get_context_data(**kwargs)
        all_entries = context['glossary'].entries.all()
        num_of_entries = context['glossary'].entries.all().count()
        context.update({
            'all_entries': all_entries,
            'num_of_entries': num_of_entries,
        })
        return context


class GlossaryExportView(LoginRequiredMixin, View):
    form_class = GlossaryExportForm
    template_name = 'glossary_export.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():

            # Get glossaries to be exported
            glossaries = form.cleaned_data.get('glossaries')

            # Create temporary folder for created glossary files to export
            export_folder = 'to_export/'
            if not os.path.isdir(export_folder):
                os.makedirs(export_folder)

            # Create one tab-delim text file for each glossary object and save to export folder
            for glossary in glossaries:
                filename = export_folder + glossary.title + '.txt'
                with open(filename, 'w') as f:
                    for entry in glossary.entries.all():
                        f.write(entry.source + '\t' + entry.target)
                        if entry.notes:
                            # Replace any newline and carriage return chars
                            new_note = entry.notes.replace('\r', ' ')
                            new_note = new_note.replace('\n', ' ')
                            new_note = new_note.replace('  ', ' ')
                            f.write('\t' + new_note)
                        f.write('\n')

            # Create zip file from all files created
            shutil.make_archive(base_name='exported_files',  # Name of the zip file to create
                                format='zip',
                                root_dir=export_folder)  # Path of the directory to compress

            # Add zip file to response
            download_target = 'exported_files.zip'
            response = FileResponse(open(download_target, 'rb'), as_attachment=True)
            response['Content-Disposition'] = 'filename=exported_files'

            # Delete folder containing glossary files created for export
            shutil.rmtree(export_folder)
            # Delete zip file
            os.remove(download_target)

            # Cause the browser to download the zip file
            return response

        return render(request, self.template_name, {'form': form})
