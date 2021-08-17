import csv
from django.views.generic import (
    TemplateView, ListView, DetailView, UpdateView, DeleteView, CreateView
)
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Entry, CsvUploadFile
from .forms import CsvUploadForm


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        # to populate dropdown resources menu
        resources = Entry.objects.values_list('resource', flat=True).distinct()
        # get the last ten entries added
        recent_terms = Entry.objects.all().order_by('-id')[:10]
        context = super(HomePageView, self).get_context_data(**kwargs)
        context.update({
            'resources': resources,
            'recent_terms': recent_terms
        })
        return context


class SearchResultsView(LoginRequiredMixin, ListView):
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
                Q(resource__iexact=resource),
                Q(source__icontains=query) | Q(target__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        query = self.request.GET.get('query').strip()
        target_resource = self.request.GET.get('resource')
        resources = Entry.objects.values_list('resource', flat=True).distinct()
        hits = self.get_queryset().count()
        context.update({
            'target_resource': target_resource,
            'resources': resources,
            'hits': hits,
            'query': query
        })
        return context


class EntryDetailView(LoginRequiredMixin, DetailView):
    model = Entry
    template_name = 'entry_detail.html'


class EntryCreateView(LoginRequiredMixin, CreateView):
    model = Entry
    template_name = 'entry_create.html'
    fields = ('source', 'target', 'resource', 'notes')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class EntryUpdateView(LoginRequiredMixin, UpdateView):
    model = Entry
    template_name = 'entry_update.html'
    fields = ('source', 'target', 'resource', 'notes')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class EntryDeleteView(LoginRequiredMixin, DeleteView):
    model = Entry
    template_name = 'entry_delete.html'
    success_url = reverse_lazy('home')


def check_row_content(row):
    ''' Helper function for glossary_upload() '''
    # Each row should contain 2 or 3 elements
    if (len(row) < 2) or (len(row) > 3):
        return False
    # Check whether identical record already exists in the DB
    if Entry.objects.filter(source=row[0], target=row[1]).exists():
        return False
    return True


@login_required
def glossary_upload(request):
    if request.method == "POST":
        form = CsvUploadForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            csv_file = CsvUploadFile.objects.latest("uploaded_on")

            with open(csv_file.file_name.path, "r") as f:
                reader = csv.reader(f, delimiter='\t')
                for row in reader:

                    # Only add to DB if row content passes checks
                    verified = check_row_content(row)
                    if verified:

                        # Handling for optional notes item
                        if len(row) == 3:
                            notes = row[2]
                        else:
                            notes = ''

                        # Add to DB
                        Entry.objects.create(
                            source=row[0],
                            target=row[1],
                            resource=csv_file.glossary_title,
                            notes=notes,
                            created_on=timezone.now(),
                            created_by=request.user,
                            updated_on=timezone.now(),
                            updated_by=request.user,
                        )

            # Delete the uploaded csv file after DB entry created
            csv_file.delete()

            return redirect("home")

    else:
        form = CsvUploadForm()
    return render(request, "glossary_upload.html", {"form": form})
