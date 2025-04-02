from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from .forms import PostForm, MediaForm
from .models import Post
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, get_object_or_404

# Create your views here.
@login_required
def home(request):
    return render(request, 'photonest/base/base.html')

@login_required
def gallery(request):
    if request.method == 'POST':
        return create_post(request)
    else:
        post_form, media_formset = create_post(request)
        return render(request, 'photonest/sites/gallery.html', {"posts": Post.objects.all(), "post_form": post_form, "media_formset": media_formset})

@login_required
def create_post(request):
    MediaFormSet = formset_factory(MediaForm, extra=1, max_num=5)
    
    if request.method == 'POST':
        post_form = PostForm(request.POST, user=request.user)
        media_formset = MediaFormSet(request.POST, request.FILES)
        if post_form.is_valid() and media_formset.is_valid():
            post = post_form.save()
            for form in media_formset:
                if form.cleaned_data.get('media_file'):
                    media = form.save(commit=False)
                    media.save()
                    post.media_files.add(media)
        return redirect('gallery')
    else:
        post_form = PostForm(user=request.user)
        media_formset = MediaFormSet()
        return post_form, media_formset,

@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    
    if 'like' in request.POST:
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
        else:
            post.likes.add(user)
    
    return redirect('gallery')