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
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    keywords = models.CharField(max_length=300, blank=True)  # for search
    summary = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.title
class ArticleFile(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='articles/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.article.title} → {self.file.name.split('/')[-1]}"
class Reference(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='references')
    citation_text = models.TextField()
    citation_style = models.CharField(
        max_length=50,
        choices=[('APA', 'APA'), ('MLA', 'MLA'), ('Chicago', 'Chicago')]
    )
    author = models.CharField(max_length=255, blank=True)
    year = models.CharField(max_length=10, blank=True)
    source = models.CharField(max_length=255, blank=True)
    linked_excerpt = models.TextField(blank=True, help_text="The excerpt or section this citation is linked to")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.citation_text} ({self.citation_style})"


class Note(models.Model):
    content = models.TextField()
    page_number = models.IntegerField(blank=True, null=True)

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="notes")
    file = models.ForeignKey(ArticleFile, on_delete=models.CASCADE, related_name="notes", null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note by {self.created_by} on {self.article}"