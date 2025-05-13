from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Project(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=300)
    abstract = models.TextField(blank=True)
    file = models.FileField(upload_to='articles/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    keywords = models.CharField(max_length=300, blank=True)  # for search

    def __str__(self):
        return self.title

class Reference(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='references')
    citation_text = models.TextField()
    citation_style = models.CharField(
        max_length=50,
        choices=[('APA', 'APA'), ('MLA', 'MLA'), ('Chicago', 'Chicago')]
    )
    created_at = models.DateTimeField(auto_now_add=True)

class Note(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    page_number = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
