import os
import csv
import shutil
from itertools import chain

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
    GlossaryExportForm, TranslationUploadForm
)
from .models import (
    Entry, Glossary, Segment, Translation
)

from translate.storage.tmx import tmxfile  # For reading tmx files (from translate-toolkit)


class ResourceListMixin(ContextMixin, View):
    """
    Class used to populate the resources dropdown list.
    Implemented as a base class to avoid repeating in each view.
    """
    def get_context_data(self, **kwargs):
        glossaries = Glossary.objects.all().order_by(Lower("title"))
        translations = Translation.objects.all().order_by(Lower("job_number"))
        resources = chain(glossaries, translations)
        context = super().get_context_data(**kwargs)
        context["resources"] = resources
        return context


class HomePageView(LoginRequiredMixin, ResourceListMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        # Get all available glossaries and translations and add to the context
        glossaries = Glossary.objects.all().order_by("-id")
        translations = Translation.objects.all().order_by("-id")
        context = super(HomePageView, self).get_context_data(**kwargs)
        context.update({
            "glossaries": glossaries,
            "translations": translations,
        })
        return context


class SearchResultsView(LoginRequiredMixin, ResourceListMixin, ListView):
    model = Entry
    template_name = "search_results.html"

    def get_queryset(self):
        query = self.request.GET.get("query").strip()
        resource = self.request.GET.get("resource")

        if resource == "すべてのリソースを検索する":
            glossary_queryset = Entry.objects.filter(
                Q(source__icontains=query) | Q(target__icontains=query)
            )
            translation_queryset = Segment.objects.filter(
                Q(source__icontains=query) | Q(target__icontains=query)
            )
        else:
            glossary_queryset = Entry.objects.filter(
                Q(glossary__title=resource),
                Q(source__icontains=query) | Q(target__icontains=query)
            )
            translation_queryset = Segment.objects.filter(
                Q(translation__job_number=resource),
                Q(source__icontains=query) | Q(target__icontains=query)
            )

        queryset = list(chain(glossary_queryset, translation_queryset))

        return queryset

    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        query = self.request.GET.get("query").strip()
        target_resource = self.request.GET.get("resource")
        hits = len(self.get_queryset())
        context.update({
            "target_resource": target_resource,
            "hits": hits,
            "query": query
        })
        return context


class EntryDetailView(LoginRequiredMixin, DetailView):
    model = Entry
    template_name = "entry_detail.html"


class EntryCreateView(LoginRequiredMixin, CreateView):
    model = Entry
    form_class = CreateEntryForm
    template_name = "entry_create.html"

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

        if self.request.GET.get("previous_url"):
            previous_url = self.request.GET.get("previous_url")
            return HttpResponseRedirect(previous_url)

        return HttpResponseRedirect(obj.get_absolute_url())

    def post(self, request, *args, **kwargs):
        """Over-ridden to check if the cancel button has been pressed
           instead of the submit button on the update form."""
        if "cancel" in request.POST:
            if request.GET.get("previous_url"):
                previous_url = request.GET.get("previous_url")
                return HttpResponseRedirect(previous_url)
        else:
            return super(EntryCreateView, self).post(request, *args, **kwargs)


class EntryUpdateView(LoginRequiredMixin, UpdateView):
    model = Entry
    template_name = "entry_update.html"
    fields = ("source", "target", "glossary", "notes")

    def form_valid(self, form):
        """Sets the updated_by field to the current user,
           and sets the previous url as the success url if previous_url is present."""
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.save()

        if self.request.GET.get("previous_url"):
            previous_url = self.request.GET.get("previous_url")
            return HttpResponseRedirect(previous_url)

        return HttpResponseRedirect(obj.get_absolute_url())

    def post(self, request, *args, **kwargs):
        # If the cancel button has been pressed in the form, return to the previous URL
        if "cancel" in request.POST:
            if request.GET.get("previous_url"):
                previous_url = request.GET.get("previous_url")
                return HttpResponseRedirect(previous_url)
        else:
            return super(EntryUpdateView, self).post(request, *args, **kwargs)


class EntryDeleteView(LoginRequiredMixin, DeleteView):
    model = Entry
    template_name = "entry_delete.html"

    def get_success_url(self):
        if self.request.GET.get("previous_url"):
            previous_url = self.request.GET.get("previous_url")
            return previous_url

        return reverse_lazy("home")

    def post(self, request, *args, **kwargs):
        # If the cancel button has been pressed in the form, return to the previous URL
        if "cancel" in request.POST:
            if request.GET.get("previous_url"):
                previous_url = request.GET.get("previous_url")
                return HttpResponseRedirect(previous_url)
        else:
            return super(EntryDeleteView, self).post(request, *args, **kwargs)


class GlossaryUploadView(LoginRequiredMixin, View):
    form_class = GlossaryUploadForm
    template_name = "glossary_upload.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):

        # If the cancel button has been pressed in the form, return to the previous URL
        if "cancel" in request.POST:
            if request.GET.get("previous_url"):
                previous_url = request.GET.get("previous_url")
                return HttpResponseRedirect(previous_url)

        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            glossary_obj = Glossary(
                glossary_file=form.cleaned_data["glossary_file"],
                title=form.cleaned_data["title"],
                notes=form.cleaned_data["notes"],
                created_by=request.user,
                updated_by=request.user,
            )
            glossary_obj.save()
            build_entries(glossary_obj, request)

            # Return to the previous URL if included in request
            if request.GET.get("previous_url"):
                previous_url = request.GET.get("previous_url")
                return HttpResponseRedirect(previous_url)

            return redirect("home")

        return render(request, self.template_name, {"form": form})


def build_entries(glossary_obj, request):
    """
    Helper method for GlossaryUploadView.
    Builds Entry objects from the content of an uploaded text file.
    Receives new Glossary object.
    """
    new_entries = []
    f = glossary_obj.glossary_file.open("r")
    reader = csv.reader(f, delimiter="\t")

    # Loop for creating new Entry objects from content of uploaded file
    for row in reader:
        # Each row should contain 2 or 3 elements, otherwise ignored
        if (len(row) == 2) or (len(row) == 3):
            # Handling for optional notes item
            if len(row) == 3:
                notes = row[2]
            else:
                notes = ""
            # Create Entry object and append to new_entries list
            new_entry = Entry(
                source=row[0],
                target=row[1],
                glossary=glossary_obj,
                notes=notes,
                created_on=timezone.now(),
                created_by=request.user,
                updated_on=timezone.now(),
                updated_by=request.user,
            )
            new_entries.append(new_entry)

    # Add all new Entry objects to the database in one write
    Entry.objects.bulk_create(new_entries)

    # Delete the uploaded text file after new Entry objects have been saved to DB
    glossary_obj.glossary_file.delete()


class GlossaryDetailView(LoginRequiredMixin, DetailView):
    model = Glossary
    template_name = "glossary_detail.html"

    def get_context_data(self, **kwargs):
        context = super(GlossaryDetailView, self).get_context_data(**kwargs)
        num_of_entries = context["glossary"].entries.all().count()
        context.update({
            "num_of_entries": num_of_entries,
        })
        return context


class GlossaryCreateView(LoginRequiredMixin, CreateView):
    model = Glossary
    form_class = CreateGlossaryForm
    template_name = "glossary_create.html"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.updated_by = self.request.user
        obj.save()

        if self.request.GET.get("previous_url"):
            previous_url = self.request.GET.get("previous_url")
            return HttpResponseRedirect(previous_url)

        return HttpResponseRedirect(obj.get_absolute_url())

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            if request.GET.get("previous_url"):
                previous_url = request.GET.get("previous_url")
                return HttpResponseRedirect(previous_url)
        else:
            return super(GlossaryCreateView, self).post(request, *args, **kwargs)


class GlossaryDeleteView(LoginRequiredMixin, DeleteView):
    model = Glossary
    template_name = "glossary_delete.html"
    success_url = reverse_lazy("home")


class GlossaryAddEntryView(LoginRequiredMixin, CreateView):
    """
    Class to add a new Entry object to an existing Glossary Object.
    Called from the Glossary detail page.
    Receives pk of Glossary object in question and sets this for the entry.glossary field.
    """
    model = Entry
    form_class = AddEntryToGlossaryForm
    template_name = "glossary_add_entry.html"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.glossary = Glossary.objects.get(pk=self.kwargs["glossary"])
        obj.created_by = self.request.user
        obj.updated_by = self.request.user
        obj.save()

        if self.request.GET.get("previous_url"):
            previous_url = self.request.GET.get("previous_url")
            return HttpResponseRedirect(previous_url)

        return HttpResponseRedirect(obj.get_absolute_url())

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            if request.GET.get("previous_url"):
                previous_url = request.GET.get("previous_url")
                return HttpResponseRedirect(previous_url)
        else:
            return super(GlossaryAddEntryView, self).post(request, *args, **kwargs)


class GlossaryUpdateView(LoginRequiredMixin, UpdateView):
    model = Glossary
    template_name = "glossary_update.html"
    fields = ("title", "notes")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class GlossaryAllEntryView(LoginRequiredMixin, DetailView):
    model = Glossary
    template_name = "glossary_all.html"

    def get_context_data(self, **kwargs):
        context = super(GlossaryAllEntryView, self).get_context_data(**kwargs)
        all_entries = context["glossary"].entries.all()
        num_of_entries = context["glossary"].entries.all().count()
        context.update({
            "all_entries": all_entries,
            "num_of_entries": num_of_entries,
        })
        return context


class GlossaryExportView(LoginRequiredMixin, View):
    form_class = GlossaryExportForm
    template_name = "glossary_export.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):

        # If the cancel button has been pressed in the form, return to the previous URL
        if "cancel" in request.POST:
            if request.GET.get("previous_url"):
                previous_url = request.GET.get("previous_url")
                return HttpResponseRedirect(previous_url)

        form = self.form_class(request.POST)
        if form.is_valid():
            glossaries = form.cleaned_data.get("glossaries")  # Glossary objects to be exported
            response = build_download(glossaries)
            return response

        return render(request, self.template_name, {"form": form})


def build_download(glossaries):
    """
    Helper function for GlossaryExportView.
    Receives list of Glossary objects.
    Converts each object into a text file.
    Zips all the text files together.
    Returns a FileResponse that causes the browser to download the zip file.
    """

    # Create local temporary folder to hold glossary files to be exported
    export_folder = "to_export/"
    if not os.path.isdir(export_folder):
        os.makedirs(export_folder)

    # Create one tab-delim text file for each Glossary object and save to temporary folder
    for glossary in glossaries:
        filename = export_folder + glossary.title + ".txt"
        with open(filename, "w") as f:
            for entry in glossary.entries.all():
                f.write(entry.source + "\t" + entry.target)
                if entry.notes:
                    # Replace any newline and carriage return chars and append note
                    new_note = entry.notes.replace("\r", " ")
                    new_note = new_note.replace("\n", " ")
                    new_note = new_note.replace("  ", " ")
                    f.write("\t" + new_note)
                f.write("\n")

    # Create single zip file from all files created
    shutil.make_archive(base_name="exported_files",  # Name of the zip file to create
                        format="zip",
                        root_dir=export_folder)  # Path of the directory to compress

    # Add zip file to response
    download_target = "exported_files.zip"
    response = FileResponse(open(download_target, "rb"), as_attachment=True)
    # Force browser to download
    response["Content-Disposition"] = "filename=exported_files"

    # Delete local temporary folder containing created glossary files
    shutil.rmtree(export_folder)
    # Delete local zip file
    os.remove(download_target)

    return response


class TranslationDetailView(LoginRequiredMixin, DetailView):
    model = Translation
    template_name = "translation_detail.html"

    def get_context_data(self, **kwargs):
        context = super(TranslationDetailView, self).get_context_data(**kwargs)
        num_of_segments = context["translation"].segments.all().count()
        context.update({
            "num_of_segments": num_of_segments,
        })
        return context


class TranslationUpdateView(LoginRequiredMixin, UpdateView):
    model = Translation
    template_name = "translation_update.html"
    fields = ("job_number", "field", "client", "notes")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())


class TranslationDeleteView(LoginRequiredMixin, DeleteView):
    model = Translation
    template_name = "translation_delete.html"
    success_url = reverse_lazy("home")


class TranslationShowAllView(LoginRequiredMixin, DetailView):
    model = Translation
    template_name = "translation_all.html"

    def get_context_data(self, **kwargs):
        context = super(TranslationShowAllView, self).get_context_data(**kwargs)
        all_segs = context["translation"].segments.all()
        num_of_segments = context["translation"].segments.all().count()
        context.update({
            "all_segs": all_segs,
            "num_of_segments": num_of_segments,
        })
        return context


class TranslationUploadView(LoginRequiredMixin, View):
    form_class = TranslationUploadForm
    template_name = "translation_upload.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):

        # If the cancel button has been pressed in the form, return to the previous URL
        if "cancel" in request.POST:
            if request.GET.get("previous_url"):
                previous_url = request.GET.get("previous_url")
                return HttpResponseRedirect(previous_url)

        form = TranslationUploadForm(request.POST, request.FILES)
        if form.is_valid():
            translation_obj = Translation(
                translation_file=form.cleaned_data["translation_file"],
                job_number=form.cleaned_data["job_number"],
                field=form.cleaned_data["field"],
                client=form.cleaned_data["client"],
                notes=form.cleaned_data["notes"],
                uploaded_by=request.user,
            )
            translation_obj.save()
            build_segments(translation_obj)

            # Return to the previous URL if included in request
            if request.GET.get("previous_url"):
                previous_url = request.GET.get("previous_url")
                return HttpResponseRedirect(previous_url)

            return redirect("home")

        return render(request, self.template_name, {"form": form})


def build_segments(translation_obj):
    """
    Helper method for TranslationUploadView.
    Builds Segment objects from the content of an uploaded tmx file.
    Receives new Translation object.
    Uses "tmxfile" from translate-toolkit for parsing a tmx file.
    """
    new_segments = []
    tmx_file = tmxfile(translation_obj.translation_file)
    for node in tmx_file.unit_iter():
        new_segment = Segment(
            translation=translation_obj,
            source=node.source,
            target=node.target,
        )
        new_segments.append(new_segment)
    Segment.objects.bulk_create(new_segments)
    translation_obj.translation_file.delete()  # File no longer needed
