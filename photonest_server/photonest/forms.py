from django import forms
from django.core.validators import FileExtensionValidator
from .models import Post, Media, SchoolClass

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return [single_file_clean(data, initial)]

class PostForm(forms.ModelForm):
    media_files = MultipleFileField(
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'mp4', 'mov'])],
        required=False,
        label='Medien (Mehrfachauswahl möglich)'
    )

    class Meta:
        model = Post
        fields = ['school_class', 'description']

class ReportForm(forms.Form):
    reason = forms.CharField(
        label='Begründung',
        widget=forms.Textarea(attrs={'placeholder': 'Warum melden Sie diesen Inhalt?', 'rows': 4}),
        max_length=255
    )