import os
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, render
from .models import Article, ArticleFile, Note, Project, User
from django.db.models import Q
import bibtexparser
from .forms import ArticleUploadForm, BibTeXUploadForm, NoteForm, CitationForm
from .models import Reference, Article
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import FileResponse, Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404

def user_has_article_access(user, article):
    return user == article.uploaded_by or user.is_superuser

@login_required
def article_list(request):
    query = request.GET.get("q", "")
    project_id = request.GET.get("project")

    articles = Article.objects.all()

    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(abstract__icontains=query) |
            Q(keywords__icontains=query)
        )

    if project_id:
        articles = articles.filter(project__id=project_id)

    projects = Project.objects.all()

    return render(request, "articles/article_list.html", {
        "articles": articles,
        "projects": projects,
        "selected_project": int(project_id) if project_id else None,
        "query": query,
    })


@login_required
def import_bibtex(request):
    if request.user.get_role() == "reviewer":
        return HttpResponseForbidden("reViewers are not allowed to perform this action.")
    if request.method == "POST":
        form = BibTeXUploadForm(request.POST, request.FILES)
        if form.is_valid():
            bib_file = request.FILES["bib_file"]
            bib_data = bib_file.read().decode("utf-8")
            selected_article = form.cleaned_data["article"]

            # 🔒 Enforce security: only uploader or superuser can import
            if request.user != selected_article.uploaded_by and not request.user.is_superuser:
                return HttpResponseForbidden("You are not allowed to import citations for this article.")

            style = request.POST.get("citation_style", "APA")

            parser = bibtexparser.loads(bib_data)
            for entry in parser.entries:
                citation_text = entry.get("title", "Unknown Title")
                author = entry.get("author", "")
                year = entry.get("year", "")
                source = entry.get("journal") or entry.get("booktitle") or entry.get("publisher", "")

                Reference.objects.create(
                    article=selected_article,
                    citation_text=citation_text,
                    citation_style=style,
                    author=author,
                    year=year,
                    source=source,
                )

            messages.success(request, "BibTeX citations successfully imported.")
            return redirect("article:article_list")
    else:
        form = BibTeXUploadForm()

    return render(request, "articles/import_bibtex.html", {"form": form})

@login_required
def export_citations(request):
    format_type = request.GET.get("format", "APA").upper()
    article_id = request.GET.get("article")
    
    if article_id:
        article = get_object_or_404(Article, id=article_id)
        if not user_has_article_access(request.user, article):
            return HttpResponseForbidden("You are not allowed to export citations for this article.")
        references = article.references.filter(citation_style=format_type)
    else:
        # Optional: restrict exporting global references if needed
        references = Reference.objects.filter(citation_style=format_type, article__uploaded_by=request.user)

    citations = []
    for ref in references:
        line = f"{ref.citation_text}"
        if ref.author: line += f" by {ref.author}"
        if ref.year: line += f", {ref.year}"
        if ref.source: line += f", {ref.source}"
        citations.append(line)

    content = "\n\n".join(citations)
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{format_type.lower()}_citations.txt"'
    return response


@login_required
def export_bibtex_file(request):
    article_id = request.GET.get("article")
    references = Reference.objects.all()

    if article_id:
        article = get_object_or_404(Article, id=article_id)
        if not user_has_article_access(request.user, article):
            return HttpResponseForbidden("You are not allowed to export BibTeX for this article.")
        references = references.filter(article_id=article_id)

    lines = []
    for idx, ref in enumerate(references):
        entry = f"@misc{{ref{idx},"
        entry += f"\n  title={{ {ref.citation_text} }},"
        if ref.author: entry += f"\n  author={{ {ref.author} }},"
        if ref.year: entry += f"\n  year={{ {ref.year} }},"
        if ref.source: entry += f"\n  howpublished={{ {ref.source} }}"
        entry += "\n}"
        lines.append(entry)

    response = HttpResponse("\n\n".join(lines), content_type='application/x-bibtex')
    response['Content-Disposition'] = 'attachment; filename="citations.bib"'
    return response


@login_required
def export_ris_file(request):
    article_id = request.GET.get("article")
    references = Reference.objects.all()

    if article_id:
        article = get_object_or_404(Article, id=article_id)
        if not user_has_article_access(request.user, article):
            return HttpResponseForbidden("You are not allowed to export RIS for this article.")
        references = references.filter(article_id=article_id)

    lines = []
    for ref in references:
        lines.extend([
            "TY  - JOUR",
            f"TI  - {ref.citation_text}",
            f"AU  - {ref.author or 'Unknown'}",
            f"PY  - {ref.year or 'n.d.'}",
            f"T2  - {ref.source or 'Unknown Source'}",
            "ER  -", ""
        ])

    response = HttpResponse("\n".join(lines), content_type='application/x-research-info-systems')
    response['Content-Disposition'] = 'attachment; filename="citations.ris"'
    return response


@login_required
def export_selected_citations(request):
    citation_ids = request.GET.getlist("citation_ids")
    format_type = request.GET.get("format", "APA").upper()
    references = Reference.objects.filter(id__in=citation_ids)

    # 🔒 Check access for all referenced articles
    for ref in references:
        if not user_has_article_access(request.user, ref.article):
            return HttpResponseForbidden("You are not allowed to export one or more selected citations.")

    if format_type in ["APA", "MLA", "CHICAGO"]:
        citations = [
            f"{ref.author or 'Unknown'} ({ref.year or 'n.d.'}). {ref.citation_text}{f' {ref.source}.' if ref.source else ''}"
            for ref in references
        ]
        content = "\n\n".join(citations)
        content_type = 'text/plain'
        filename = f"{format_type.lower()}_selected_citations.txt"

    elif format_type == "BIBTEX":
        citations = [
            f"@misc{{ref{ref.id},\n  author={{ {ref.author or 'Unknown'} }},\n  year={{ {ref.year or 'n.d.'} }},\n  title={{ {ref.citation_text} }},\n  howpublished={{ {ref.source or 'Unknown Source'} }}\n}}"
            for ref in references
        ]
        content = "\n\n".join(citations)
        content_type = 'application/x-bibtex'
        filename = "selected_citations.bib"

    elif format_type == "RIS":
        lines = []
        for ref in references:
            lines.extend([
                "TY  - JOUR",
                f"AU  - {ref.author or 'Unknown'}",
                f"PY  - {ref.year or 'n.d.'}",
                f"TI  - {ref.citation_text}",
                f"JO  - {ref.source or 'Unknown Source'}",
                "ER  -", ""
            ])
        content = "\n".join(lines)
        content_type = 'application/x-research-info-systems'
        filename = "selected_citations.ris"

    else:
        return HttpResponse("Unsupported format", status=400)

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def delete_citation(request, citation_id):
    citation = get_object_or_404(Reference, id=citation_id)
    article = citation.article

    # 🔒 Check if user has permission
    if request.user != article.uploaded_by and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to delete this citation.")

    if request.method == "POST":
        citation.delete()
        messages.success(request, "Citation deleted successfully.")
        return redirect('article:article_detail', article_id=article.id)

    return redirect('article:article_detail', article_id=article.id)
ALLOWED_EXTENSIONS = ['pdf', 'txt', 'docx']
MAX_FILE_SIZE_MB = 5

@login_required
def upload_article(request):
    if request.method == 'POST':
        form = ArticleUploadForm(request.POST)
        files = request.FILES.getlist('file')

        if form.is_valid():
            for f in files:
                ext = f.name.split('.')[-1].lower()
                if ext not in ALLOWED_EXTENSIONS:
                    form.add_error(None, f"❌ {f.name} is not an allowed file type.")
                    return render(request, 'articles/upload_article.html', {'form': form})

                if f.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                    form.add_error(None, f"❌ {f.name} exceeds the {MAX_FILE_SIZE_MB}MB size limit.")
                    return render(request, 'articles/upload_article.html', {'form': form})

            article = form.save(commit=False)
            article.uploaded_by = request.user
            article.save()

            for f in files:
                ArticleFile.objects.create(article=article, file=f, uploaded_by=request.user)

            messages.success(request, "✅ Article uploaded successfully.")
            return redirect('article:article_list')
    else:
        form = ArticleUploadForm()

    return render(request, 'articles/upload_article.html', {'form': form})


@login_required
def add_article_file(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.user != article.uploaded_by and not request.user.is_staff:
        return HttpResponseForbidden("You're not allowed to add files to this article.")

    if request.method == 'POST':
        files = request.FILES.getlist('file_field')
        errors = []

        # Collect valid + invalid files
        valid_files = []
        for f in files:
            ext = f.name.split('.')[-1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                errors.append(f"❌ {f.name} is not an allowed file type.")
            elif f.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                errors.append(f"❌ {f.name} exceeds the {MAX_FILE_SIZE_MB}MB size limit.")
            else:
                valid_files.append(f)

        if errors:
            for error in errors:
                messages.error(request, error)
            # ✅ Stay on the same page and show errors
            return render(request, 'articles/add_article_file.html', {'article': article})

        # ✅ Save valid files
        for f in valid_files:
            ArticleFile.objects.create(article=article, file=f, uploaded_by=request.user)

        messages.success(request, "✅ Files uploaded successfully.")
        return redirect('article:article_detail', article_id=article.id)

    return render(request, 'articles/add_article_file.html', {'article': article})


@login_required
def edit_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    # 🔒 Only the uploader or a superuser can edit
    if request.user != article.uploaded_by and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to edit this article.")

    if request.method == 'POST':
        form = ArticleUploadForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('article:article_list')
    else:
        form = ArticleUploadForm(instance=article)

    return render(request, 'articles/edit_article.html', {
        'form': form,
        'article': article
    })

@login_required
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    # 🔒 Only the uploader or a superuser can delete
    if request.user != article.uploaded_by and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to delete this article.")

    if request.method == 'POST':
        article.delete()
        return redirect('article:article_list')

    return render(request, 'articles/delete_article.html', {
        'article': article
    })

@login_required
def delete_article_file(request, file_id):
    file = get_object_or_404(ArticleFile, id=file_id)
    article = file.article

    # 🔐 Only the uploader of the article or a superuser can delete
    if request.user != article.uploaded_by and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to delete this file.")

    file.file.delete()  # Delete from media folder
    file.delete()       # Delete the DB record
    messages.success(request, "File deleted successfully.")
    return redirect('article:article_detail', article_id=article.id)

@login_required
def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    notes = article.notes.all().order_by("created_at")
    references = article.references.all().order_by("created_at")

    note_form = NoteForm()

    return render(request, 'articles/article_detail.html', {
        'article': article,
        'notes': notes,
        'references': references,
        'note_form': note_form,
        'citation_form': CitationForm,
    })

def download_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if not article.file:
        raise Http404("File not attached.")

    file_path = article.file.path
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    else:
        raise Http404("File not found.")

@login_required
def add_note(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.user.get_role() == "reviewer":
        return HttpResponseForbidden("reViewers are not allowed to perform this action.")
    if request.method == 'POST':
        form = NoteForm(request.POST)
        form.fields['file'].queryset = article.files.all()  # ✅ restrict to this article's files

        if form.is_valid():
            note = form.save(commit=False)
            note.article = article
            note.created_by = request.user
            note.save()
            return redirect('article:article_detail', article_id=article.id)
    else:
        form = NoteForm()
        form.fields['file'].queryset = article.files.all()

    return render(request, 'articles/add_note.html', {
        'form': form,
        'article': article
    })

@login_required
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)

    # 🔒 Restrict access to note owner or superuser
    if note.created_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to edit this note.")

    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        form.fields['file'].queryset = note.article.files.all()  # restrict to article files

        if form.is_valid():
            form.save()
            return redirect('article:article_detail', article_id=note.article.id)
    else:
        form = NoteForm(instance=note)
        form.fields['file'].queryset = note.article.files.all()

    return render(request, 'articles/edit_note.html', {
        'form': form,
        'note': note,
        'article': note.article
    })


@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)

    # 🔒 Restrict access to note owner or superuser
    if note.created_by != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to delete this note.")

    if request.method == 'POST':
        note.delete()
        return redirect('article:article_detail', article_id=note.article.id)

    return render(request, 'articles/confirm_delete_note.html', {
        'note': note,
        'article': note.article
    })


@login_required
def add_citation(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.user != article.uploaded_by and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to add a citation to this article.")

    if request.method == "POST":
        form = CitationForm(request.POST)
        if form.is_valid():
            citation = form.save(commit=False)
            citation.article = article
            citation.save()
            messages.success(request, "Citation added successfully.")
            return redirect('article:article_detail', article_id=article_id)
    else:
        form = CitationForm()

    return render(request, 'articles/add_citation.html', {'form': form, 'article': article})


@login_required
@require_POST
def update_summary_view(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.user != article.uploaded_by and not request.user.is_superuser:
        return HttpResponseForbidden("You are not allowed to edit this summary.")

    summary = request.POST.get("summary", "").strip()
    article.summary = summary
    article.save()
    messages.success(request, "Summary updated successfully.")
    return redirect("article:article_detail", article_id=article.id)


