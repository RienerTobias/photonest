from django.contrib import admin
from .models import SchoolClass, Post, Media

class MediaInline(admin.TabularInline):
    model = Post.media_files.through
    extra = 1
    max_num = 5
    verbose_name = "Medium"
    verbose_name_plural = "Medien"

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'media_type', 'order')
    list_filter = ('media_type',)

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'color')
    search_fields = ('class_name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    exclude = ('media_files',)
    list_display = ('id', 'user', 'school_class', 'uploaded_at', 'media_count', 'like_count', 'favorites_count')
    list_filter = ('school_class', 'uploaded_at')
    search_fields = ('user__username', 'description')
    filter_horizontal = ('likes', 'favorites')
    readonly_fields = ('uploaded_at', 'like_count', 'media_count', 'favorites_count')
    
    def favorites_count(self, obj):
        return obj.favorites.count()
    favorites_count.short_description = 'Favoriten'