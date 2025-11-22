import django_filters
from django import forms
from .models import Post, SchoolClass
from django.db.models import Count
import re


def extract_year(class_name: str):
    """Gibt die erste Ziffer als Jahrgang zurück."""
    return class_name[0] if class_name and class_name[0].isdigit() else None


def extract_department(class_name: str):
    """
    Extrahiert die Abteilung MIT dem 'H'.

    Beispiele:
    1AHIT  → HIT
    1BHWIM → HWIM
    3AHET  → HET
    1AHMBA → HMBA
    1AFME  → FME
    """
    if not class_name:
        return ""

    # z. B. HIT, HWIM, HET, FME ...
    rest = class_name[2:].lower()

    # Großbuchstaben-Blöcke finden
    if rest.startswith('h'): rest = rest[1:]

    return rest.upper()


class PostFilter(django_filters.FilterSet):
    only_favorites = django_filters.BooleanFilter(
        method='filter_favorites',
        label='Nur meine Favoriten',
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'})
    )

    only_reported = django_filters.BooleanFilter(
        method='filter_is_reported',
        label='Gemeldete Posts',
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

    year = django_filters.ChoiceFilter(
        label="Jahrgang",
        choices=[],  # wird im __init__ gesetzt
        method="filter_year",
        empty_label='Alle Jahrgänge'
    )

    department = django_filters.ChoiceFilter(
        label="Abteilung",
        choices=[],  # wird im __init__ gesetzt
        method="filter_department",
        empty_label='Alle Abteilungen'
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

    # --------------------------------------------------------------------
    #                           FILTER METHODEN  
    # --------------------------------------------------------------------

    def filter_favorites(self, queryset, name, value):
        if value and hasattr(self, 'request'):
            return queryset.filter(favorites=self.request.user)
        return queryset
    
    def filter_is_reported(self, queryset, name, value):
        if value and hasattr(self, 'request'):
            return queryset.filter(is_reported=True)
        else:
            return queryset.filter(is_reported=False)

    def filter_liked(self, queryset, name, value):
        if value and hasattr(self, 'request'):
            return queryset.filter(likes=self.request.user)
        return queryset
    
    def filter_is_used(self, queryset, name, value):
        if value and hasattr(self, 'request'):
            return queryset.filter(is_used=True)
        return queryset

    def filter_year(self, queryset, name, value):
        return queryset.filter(school_class__class_name__startswith=value)

    def filter_department(self, queryset, name, value):
        return queryset.filter(school_class__class_name__iendswith=value)

    # --------------------------------------------------------------------
    #                     AUTOMATISCHE GENERIERUNG
    # --------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Likes sortierbar machen
        self.queryset = self.queryset.annotate(_like_count=Count('likes'))

        if not self.data.get('ordering'):
            self.queryset = self.queryset.order_by('-uploaded_at')

        # Alle Klassen aus DB:
        class_names = SchoolClass.objects.values_list("class_name", flat=True)

        # 🔥 Jahrgänge dynamisch erzeugen
        years = sorted({extract_year(c) for c in class_names if extract_year(c)})
        self.filters["year"].extra["choices"] = [(y, y) for y in years]

        # 🔥 Abteilungen dynamisch erzeugen
        departments = sorted({extract_department(c) for c in class_names if extract_department(c)})
        self.filters["department"].extra["choices"] = [(d, d) for d in departments]
