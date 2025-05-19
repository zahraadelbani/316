from rest_framework import serializers
from .models import Article, ArticleFile, Reference, Note, Project
from django.contrib.auth import get_user_model

User = get_user_model()

# 🔹 User serializer (if needed for displaying uploader names/emails)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']  # add more fields if needed

# 🔹 Project serializer (optional if needed in API)
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'created_by', 'created_at']

# 🔹 File serializer now includes uploaded_by
class ArticleFileSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = ArticleFile
        fields = ['id', 'file', 'uploaded_by']

# 🔹 Citation serializer (unchanged but complete)
class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ['id', 'citation_text', 'citation_style', 'author', 'year', 'source', 'created_at']

# 🔹 Notes serializer (new)
class NoteSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    file = ArticleFileSerializer(read_only=True)

    class Meta:
        model = Note
        fields = ['id', 'content', 'page_number', 'file', 'created_by', 'created_at']

# 🔹 Main Article serializer
class ArticleSerializer(serializers.ModelSerializer):
    files = ArticleFileSerializer(many=True, read_only=True)
    references = ReferenceSerializer(many=True, read_only=True)
    notes = NoteSerializer(many=True, read_only=True)
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'abstract', 'keywords', 'project',
            'uploaded_by', 'uploaded_at', 'summary',
            'files', 'references', 'notes'
        ]
        read_only_fields = ['uploaded_by', 'uploaded_at']
