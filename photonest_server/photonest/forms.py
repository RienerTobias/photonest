from django import forms
from django.core.validators import FileExtensionValidator, MaxValueValidator, MaxLengthValidator
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

class PostEditForm(forms.ModelForm):
    new_media_files = MultipleFileField(
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'mp4', 'mov', 'svg'])],
        required=False,
        label='Neue Medien (Mehrfachauswahl möglich)'
    )
    
    class Meta:
        model = Post
        fields = ['school_class', 'description']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'textarea w-full h-24',
                'placeholder': 'Beschreibung des Posts...'
            }),
            'school_class': forms.Select(attrs={
                'class': 'select w-full rounded-full'
            })
        }
        labels = {
            'school_class': 'Klasse',
            'description': 'Beschreibung'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.post = self.instance
        self.fields['school_class'].queryset = SchoolClass.objects.all()

        self.fields['description'].validators = [
            MaxLengthValidator(500)
        ]

    def clean(self):
        cleaned_data = super().clean()
        new_media_files = self.files.getlist('new_media_files')
        current_media_count = self.post.media_files.count() if self.post else 0
        
        total_media = current_media_count + len(new_media_files)
        if total_media > 5:
            raise forms.ValidationError(
                f"Maximal 5 Medien pro Post erlaubt. "
                f"Aktuell {current_media_count} vorhanden, "
                f"{len(new_media_files)} neue ausgewählt."
            )

        for file in new_media_files:
            content_type = file.content_type
            if not content_type.startswith('image/') and not content_type.startswith('video/'):
                raise forms.ValidationError(
                    f"Ungültiger Dateityp: {content_type}. "
                    "Nur Bilder und Videos sind erlaubt."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        post = super().save(commit=False)
        
        if commit:
            post.save()
            self.save_m2m()
            
            for media_file in self.files.getlist('new_media_files'):
                media = Media.objects.create(
                    media_file=media_file,
                    media_type='photo' if media_file.content_type.startswith('image/') else 'video'
                )
                post.media_files.add(media)
        
        return post