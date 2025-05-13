from django.contrib import admin
from .models import Article, Project, Reference, Note

admin.site.register(Article)
admin.site.register(Project)
admin.site.register(Reference)
admin.site.register(Note)
