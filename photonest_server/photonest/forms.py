from django import forms
from django.core.validators import FileExtensionValidator
from .models import Post, Media, SchoolClass

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['media_file', 'media_type', 'order']
        widgets = {
            'order': forms.NumberInput(attrs={'min': 0, 'max': 4})
        }

    def clean_media_file(self):
        file = self.cleaned_data.get('media_file')
        if file:
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov']
            ext = file.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError("Nur Bild- oder Video-Dateien sind erlaubt")
        return file

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['school_class', 'description']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['school_class'].queryset = SchoolClass.objects.all()

    def save(self, commit=True):
        post = super().save(commit=False)
        if self.user:
            post.user = self.user
        if commit:
            post.save()
        return post