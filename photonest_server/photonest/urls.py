from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('gallery', views.gallery, name='gallery'),
    path('posts/<int:post_id>/like/', views.like_post, name='like_post'),
    path('posts/<int:post_id>/favor/', views.favor_post, name='favor_post'),
]
