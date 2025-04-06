import django_filters
from django import forms
from .models import Post, SchoolClass
from django.db.models import Count

class PostFilter(django_filters.FilterSet):
    only_favorites = django_filters.BooleanFilter(
        method='filter_favorites',
        label='Nur meine Favoriten',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'})
    )
    
    only_liked = django_filters.BooleanFilter(
        method='filter_liked',
        label='Nur meine Likes',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'})
    )
    
    is_used = django_filters.BooleanFilter(
        method='filter_is_used',
        label='Nur verwendete Posts',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'}),
        lookup_expr='exact'
    )
    
    school_class = django_filters.ModelChoiceFilter(
        queryset=SchoolClass.objects.all(),
        label='Klasse',
        empty_label='Alle Klassen'
    )
    
    ordering = django_filters.OrderingFilter(
        choices=[
            ('-uploaded_at', 'Neueste zuerst'),
            ('uploaded_at', 'Älteste zuerst'),
            ('-_like_count', 'Beliebteste zuerst'),
            ('_like_count', 'Am wenigsten beliebt'),
        ],
        fields={
            'uploaded_at': 'uploaded_at',
            '_like_count': '_like_count',
        },
        label='Sortierung',
        initial='-uploaded_at',
    )

    class Meta:
        model = Post
        fields = []

    def filter_favorites(self, queryset, name, value):
        if value and hasattr(self, 'request'):
            return queryset.filter(favorites=self.request.user)
        return queryset

    def filter_liked(self, queryset, name, value):
        if value and hasattr(self, 'request'):
            return queryset.filter(likes=self.request.user)
        return queryset
    
    def filter_is_used(self, queryset, name, value):
        if value and hasattr(self, 'request'):
            return queryset.filter(is_used=True)
        return queryset

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queryset = self.queryset.annotate(_like_count=Count('likes'))

        if not self.data.get('ordering'):
            self.queryset = self.queryset.order_by('-uploaded_at')