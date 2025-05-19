from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ArticleViewSet, ArticleFileViewSet, ReferenceViewSet, NoteViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'files', ArticleFileViewSet, basename='file')
router.register(r'references', ReferenceViewSet, basename='reference')
router.register(r'notes', NoteViewSet, basename='note')

urlpatterns = router.urls  # ✅ no 'api/' prefix
