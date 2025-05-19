from django.urls import path
from . import views
from django.views.generic import TemplateView
from .views import delete_article_file, upload_article, delete_article, add_note, article_detail, edit_note, delete_note

app_name = "article" 

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('import-bibtex/', views.import_bibtex, name='import_bibtex'),
    path('export-citations/', views.export_citations, name='export_citations'),
    path('export-citations.bib', views.export_bibtex_file, name='export_bibtex_file'),
    path('export-citations.ris', views.export_ris_file, name='export_ris_file'),
    path('citations/<int:citation_id>/delete/', views.delete_citation, name='delete_citation'),
    path('citations/export-selected/', views.export_selected_citations, name='export_selected_citations'),
    path('articles/<int:article_id>/add-citation/', views.add_citation, name='add_citation'),
    path('articles/<int:article_id>/update-summary/', views.update_summary_view, name='update_summary'),

    path('test-upload/', TemplateView.as_view(template_name='upload_test.html'), name='upload_test'),
    path('upload/', upload_article, name='upload_article'),
    path('articles/<int:article_id>/add-file/', views.add_article_file, name='add_article_file'),
    path('files/<int:file_id>/delete/', views.delete_article_file, name='delete_article_file'),
    path('edit/<int:article_id>/', views.edit_article, name='edit_article'),
    path('delete/<int:article_id>/', delete_article, name='delete_article'),
    path('articles/<int:article_id>/', article_detail, name='article_detail'),
    path('articles/<int:article_id>/download/', views.download_article, name='download_article'),

    path('articles/<int:article_id>/notes/add/', add_note, name='add_note'),
    path('notes/<int:note_id>/edit/', edit_note, name='edit_note'),
    path('notes/<int:note_id>/delete/', delete_note, name='delete_note'),
 
    


]
