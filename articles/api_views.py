from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Article, ArticleFile, Reference, Note
from .serializers import (
    ArticleSerializer,
    ArticleFileSerializer,
    ReferenceSerializer,
    NoteSerializer
)


from rest_framework.permissions import BasePermission

class IsNotReviewer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.get_role() != "reviewer"

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsNotReviewer]
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def update_summary(self, request, pk=None):
        article = self.get_object()
        summary = request.data.get('summary', '')

        if not summary:
            return Response({'error': 'Summary is required.'}, status=status.HTTP_400_BAD_REQUEST)

        article.summary = summary
        article.save()
        return Response({
            'message': 'Summary updated successfully.',
            'summary': article.summary
        })


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsNotReviewer]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ArticleFileViewSet(viewsets.ModelViewSet):
    queryset = ArticleFile.objects.all()
    serializer_class = ArticleFileSerializer
    permission_classes = [IsNotReviewer]


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
    permission_classes = [IsNotReviewer]
