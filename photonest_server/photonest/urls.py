from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('gallery', views.gallery, name='gallery'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('profile', views.profile, name='profile'),
    path('settings', views.settings, name='settings'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/like/', views.like_post, name='like_post'),
    path('posts/<int:post_id>/favor/', views.favor_post, name='favor_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:post_id>/download/all/', views.download_all_post_media, name='download_all_post_media'),
    path('media/<int:media_id>/download/', views.download_single_media, name='download_single_media'),
]
