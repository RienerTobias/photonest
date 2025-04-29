from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponse, FileResponse
from django.utils.timezone import now
from django.db.models import Count, Q
from .forms import PostForm
from .models import Post, Media, SchoolClass
from .filters import PostFilter
import magic
import os
import zipfile
from io import BytesIO

# Create your views here.
@login_required
def home(request):    
    return render(request, 'photonest/sites/home.html', {
        'newest_posts': Post.objects.all().order_by('-uploaded_at')[:3],
        'top_posts': Post.objects.all().annotate(_like_count=Count('likes')).order_by('-_like_count')[:3],
        'form': PostForm(),
        'create_post_url': 'home',
        'timestamp': now().timestamp(),
        'max_files': 15,
        'pageprefix': 'home',
    })

@login_required
def gallery(request):    
    filter = PostFilter(request.GET, queryset=Post.objects.all().prefetch_related('media_files'), request=request)

    if not request.GET.get('ordering'):
        filter.form.initial['ordering'] = '-uploaded_at'

    return render(request, 'photonest/sites/gallery.html', {
        'filter': filter,
        'form': PostForm(),
        'create_post_url': 'gallery',
        'timestamp': now().timestamp(),
        'max_files': 15,
        'pageprefix': 'gallery'
    })

@login_required
def dashboard(request): 
    sort_field_user = request.GET.get('sort_user', '-likes_received')
    valid_fields_user = ['username', 'uploads_count', 'likes_received', 'uses_count']
    
    if sort_field_user.lstrip('-') not in valid_fields_user:
        sort_field_user = '-likes_received'

    users = User.objects.annotate(
        uploads_count=Count('posts'),
        likes_received=Count('posts__likes'),
        uses_count=Count('posts', filter=Q(posts__is_used=True))).order_by(sort_field_user)
    
    sort_field_class = request.GET.get('sort_class', '-total_likes')
    valid_fields_class = ['class_name', 'total_uploads', 'total_likes', 'total_uses']
    
    # Sicherheitscheck für Sortierparameter
    if sort_field_class.lstrip('-') not in valid_fields_class:
        sort_field_class = '-total_likes'

    classes = SchoolClass.objects.annotate(
        total_uploads=Count('posts', distinct=True),
        total_likes=Count('posts__likes', distinct=True),
        total_uses=Count('posts', filter=Q(posts__is_used=True), distinct=True)
    ).order_by(sort_field_class)
    
    

    return render(request, 'photonest/sites/dashboard.html', {
        'users': users,
        'classes': classes,
        'current_sort_user': sort_field_user,
        'current_sort_class': sort_field_class,
        'timestamp': now().timestamp(),
    })

@login_required
def profile(request):    
    user = request.user

    return render(request, 'photonest/sites/profile.html', {
        'post_count': user.posts.count(),
        'like_count': user.posts.aggregate(total_likes=Count('likes'))['total_likes'],
        'used_count': user.posts.filter(is_used=True).count(),
        'timestamp': now().timestamp(),
    })

@login_required
@require_POST
def create_post(request):
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        print("valid")
        post = form.save(commit=False)
        post.user = request.user
        post.save()
        
        for file in request.FILES.getlist('media_files'):
            mime = magic.Magic(mime=True)
            content_type = mime.from_buffer(file.read(1024))
            file.seek(0)
            
            media_type = 'photo' if content_type.startswith('image/') else 'video'
            
            media = Media.objects.create(
                media_file=file,
                media_type='photo' if content_type.startswith('image/') else 'video'
            )
            post.media_files.add(media) 
        
    return redirect(request.POST.get('next', 'home'))

@login_required
@require_POST
@csrf_exempt 
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    
    if user == post.user:
        return JsonResponse({
        'status': 'unliked',
        'like_count': post.likes.count()
    })

    if post.likes.filter(id=user.id).exists():
        post.likes.remove(user)
        status = 'unliked'
    else:
        post.likes.add(user)
        status = 'liked'
    
    return JsonResponse({
        'status': status,
        'like_count': post.likes.count()
    })

@login_required
@require_POST
@csrf_exempt
@permission_required('photonest.favor_post')
def favor_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    
    if post.favorites.filter(id=user.id).exists():
        post.favorites.remove(user)
        status = 'false'
    else:
        post.favorites.add(user)
        status = 'true'
    
    return JsonResponse({
        'favored': status,
    })

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.user == post.user or request.user.is_superuser or request.user.has_perm('favor_post'):
        post.delete()
    
    return redirect(request.POST.get('next', 'home'))

@login_required
def download_all_post_media(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    media_files = post.media_files.all()

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for media in media_files:
            file_path = media.media_file.path
            zipf.write(file_path, os.path.basename(file_path))

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="post_{post_id}_media.zip"'
    post.mark_as_used()
    return response

@login_required
def download_single_media(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    file_path = media.media_file.path

    related_posts = media.posts.all()
    for post in related_posts:
        post.mark_as_used()
    return FileResponse(open(file_path, 'rb'), as_attachment=True)