from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator

class SchoolClass(models.Model):
    class_name = models.CharField(max_length=10, unique=True, verbose_name="Klassenname")
    color = ColorField(samples=[
        ("#015AAA", "blue"), ("#EE3D3C", "red"), ("#FEC210", "yellow"),
        ("#F7931D", "orange"), ("#8BC63E", "green"),
    ])
    
    class Meta:
        verbose_name = "Schulklasse"
        verbose_name_plural = "Schulklassen"
        ordering = ['class_name']
    
    def __str__(self):
        return self.class_name

class Media(models.Model):
    MEDIA_TYPE_CHOICES = [('photo', 'Foto'), ('video', 'Video')]
    
    media_file = models.FileField(upload_to='photonest/%Y/%m/%d/')
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPE_CHOICES)
    order = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)])
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.get_media_type_display()} #{self.order}"

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    media_files = models.ManyToManyField(Media, related_name='posts')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_posts', blank=True)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name='posts')
    description = models.TextField(max_length=500, blank=False)
    uploaded_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)
    used_in = models.CharField(max_length=100, blank=True, null=True)
    used_at = models.DateTimeField(blank=True, null=True)
    
    @property
    def like_count(self): return self.likes.count()
    @property
    def media_count(self): return self.media_files.count()
    @property
    def is_favorite(self, user): return self.favorites.filter(id=user.id).exists()
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Post #{self.id} von {self.user.username}"