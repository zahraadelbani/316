from django import forms

class BibTeXUploadForm(forms.Form):
    bib_file = forms.FileField(label="Upload BibTeX File")
