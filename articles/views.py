from django.shortcuts import render
from .models import Article, Project
from django.db.models import Q
import bibtexparser
from .forms import BibTeXUploadForm
from .models import Reference, Article
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse

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
    if request.method == "POST":
        form = BibTeXUploadForm(request.POST, request.FILES)
        if form.is_valid():
            bib_file = request.FILES["bib_file"]
            bib_data = bib_file.read().decode("utf-8")

            parser = bibtexparser.loads(bib_data)
            for entry in parser.entries:
                citation_text = entry.get("title", "Unknown Title")
                style = "APA"  # You can update later based on user choice

                # Dummy article link for now — improve later
                dummy_article = Article.objects.first()

                Reference.objects.create(
                    article=dummy_article,
                    citation_text=citation_text,
                    citation_style=style
                )
            return redirect("article_list")
    else:
        form = BibTeXUploadForm()

    return render(request, "articles/import_bibtex.html", {"form": form})

def export_citations(request):
    format_type = request.GET.get("format", "APA").upper()

    # Filter by format (APA/MLA/Chicago)
    references = Reference.objects.filter(citation_style=format_type)

    citations = [ref.citation_text for ref in references]

    return JsonResponse({
        "format": format_type,
        "citations": citations
    })

def export_bibtex_file(request):
    references = Reference.objects.all()
    lines = []

    for idx, ref in enumerate(references):
        lines.append(f"@misc{{ref{idx},\n  title={{ {ref.citation_text} }}\n}}\n")

    response = HttpResponse("\n".join(lines), content_type='application/x-bibtex')
    response['Content-Disposition'] = 'attachment; filename="citations.bib"'
    return response

def export_ris_file(request):
    references = Reference.objects.all()
    lines = []

    for ref in references:
        lines.extend([
            "TY  - JOUR",
            f"TI  - {ref.citation_text}",
            "ER  -",
            ""
        ])

    response = HttpResponse("\n".join(lines), content_type='application/x-research-info-systems')
    response['Content-Disposition'] = 'attachment; filename="citations.ris"'
    return response
