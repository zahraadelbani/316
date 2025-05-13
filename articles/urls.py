from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('import-bibtex/', views.import_bibtex, name='import_bibtex'),
    path('export-citations/', views.export_citations, name='export_citations'),
    path('export-citations.bib', views.export_bibtex_file, name='export_bibtex_file'),
    path('export-citations.ris', views.export_ris_file, name='export_ris_file'),
]
