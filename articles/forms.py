from django import forms
from .models import Article, ArticleFile, Note, Reference

class BibTeXUploadForm(forms.Form):
    article = forms.ModelChoiceField(
        queryset=Article.objects.all(),
        label="Select Article",
        widget=forms.Select(attrs={
            'class': 'w-full p-2 border rounded'
        })
    )
    bib_file = forms.FileField(
        label="Upload BibTeX File",
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full p-2 border rounded'
        })
    )

class ArticleUploadForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'title',
            'authors',
            'journal_conference',
            'publication_year',
            'doi',
            'abstract',
            'keywords',
            'project',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'authors': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded',
                'placeholder': 'e.g. Alice Smith; Bob Jones'
            }),
            'journal_conference': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded',
                'placeholder': 'Journal or Conference Name'
            }),
            'publication_year': forms.NumberInput(attrs={
                'class': 'w-full p-2 border rounded',
                'min': 1900, 'max': 2100
            }),
            'doi': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded',
                'placeholder': '10.xxxx/xxxxx'
            }),
            'abstract': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full p-2 border rounded'
            }),
            'keywords': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'project': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content', 'page_number', 'file']  # ✅ include file
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write your note here...',
                'class': 'w-full p-2 border rounded',
            }),
            'page_number': forms.NumberInput(attrs={
                'placeholder': 'Page # (optional)',
                'class': 'w-full p-2 border rounded',
            }),
            'file': forms.Select(attrs={
                'class': 'w-full p-2 border rounded',
            }),
        }
class CitationForm(forms.ModelForm):
    class Meta:
        model = Reference
        fields = ['citation_text', 'citation_style', 'author', 'year', 'source', 'linked_excerpt']
        widgets = {
            'citation_text': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'citation_style': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'author': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'year': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'source': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'linked_excerpt': forms.Textarea(attrs={'rows': 2, 'class': 'w-full p-2 border rounded', 'placeholder': 'Text or section the citation supports'}),

        }