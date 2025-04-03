from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.forms import formset_factory
from django.http import JsonResponse
from .forms import PostForm
from .models import Post, Media
import magic

# Create your views here.
@login_required
def home(request):
    return render(request, 'photonest/base/base.html')

@login_required
def gallery(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            
            # Medien verarbeiten
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
            
            return redirect('gallery')
    else:
        form = PostForm()
    
    posts = Post.objects.all().prefetch_related('media_files')
    return render(request, 'photonest/sites/gallery.html', {
        'posts': posts,
        'form': form
    })

@require_POST
@csrf_exempt  # Nur wenn Sie CSRF über Header handhaben
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    
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

@require_POST
@csrf_exempt  # Nur wenn Sie CSRF über Header handhaben
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