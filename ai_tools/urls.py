from django.urls import path
from . import views

app_name = 'ai_tools'

urlpatterns = [
    path('', views.ai_tools_page, name='ai_tools_page'),
    path('generate-summary/', views.generate_summary, name='generate_summary'),
    path('generate-citation/', views.generate_citation, name='generate_citation'),
] 