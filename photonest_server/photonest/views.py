from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponse, FileResponse
from django.utils.timezone import now
from django.utils import timezone
from datetime import datetime
from django.db.models import Count, Q
from .forms import PostForm, ReportForm, PostEditForm
from .models import Post, Media, SchoolClass
from .filters import PostFilter
import magic
import os
import zipfile
from io import BytesIO
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.conf import settings as django_settings
from django.template.loader import render_to_string

# Create your views here.
@login_required
def home(request):  
    
    return render(request, 'photonest/sites/home.html', {
        'newest_posts': Post.objects.filter(is_reported=False).order_by('-uploaded_at')[:3],
        'top_posts': Post.objects.filter(is_reported=False).annotate(_like_count=Count('likes')).order_by('-_like_count')[:3],
        'create_post_form': PostForm(),
        'report_form': ReportForm(),
        'create_post_url': 'home',
        'timestamp': now().timestamp(),
        'max_files': 15,
        'pageprefix': 'home',
        'reported_post_count': Post.objects.filter(is_reported=True).count(),
        'show_alert': request.session.pop('show_alert', False),
        'alert_message': request.session.pop('alert_message', ""),
        'alert_icon': request.session.pop('alert_icon', ""),
        'alert_type': request.session.pop('alert_type', ""),
    })

@login_required
def gallery(request):    
    filter = PostFilter(request.GET, queryset=Post.objects.all().prefetch_related('media_files'), request=request)

    if not request.GET.get('ordering'):
        filter.form.initial['ordering'] = '-uploaded_at'

    paginator = Paginator(filter.qs, django_settings.PAGINATION_LIMIT)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    return render(request, 'photonest/sites/gallery.html', {
        'filter': filter,
        'page_obj': page_obj,
        'form': PostForm(),
        'create_post_url': 'gallery',
        'create_post_form': PostForm(),
        'report_form': ReportForm(),
        'timestamp': now().timestamp(),
        'max_files': 15,
        'pageprefix': 'gallery',
        'reported_post_count': Post.objects.filter(is_reported=True).count(),
        'show_alert': request.session.pop('show_alert', False),
        'alert_message': request.session.pop('alert_message', ""),
        'alert_icon': request.session.pop('alert_icon', ""),
        'alert_type': request.session.pop('alert_type', ""),
    })

@login_required
def gallery_load_more(request):
    page = request.GET.get("page", 1)

    qs = Post.objects.all().prefetch_related('media_files')
    filter = PostFilter(request.GET, queryset=qs, request=request)

    paginator = Paginator(filter.qs, django_settings.PAGINATION_LIMIT)
    page_obj = paginator.get_page(page)

    html = render_to_string("photonest/elements/gallery_posts.html", {
        "page_obj": page_obj
    }, request=request)
    
    return JsonResponse({
        "html": html,
        "has_next": page_obj.has_next(),
        "next_page": page_obj.next_page_number() if page_obj.has_next() else None
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
    
    if sort_field_class.lstrip('-') not in valid_fields_class:
        sort_field_class = '-total_likes'

    current_date = now()
    if current_date.month >= 9:
        schuljahr_start = datetime(current_date.year, 9, 1)
        schuljahr_ende = datetime(current_date.year + 1, 8, 31)
    else:
        schuljahr_start = datetime(current_date.year - 1, 9, 1)
        schuljahr_ende = datetime(current_date.year, 8, 31)
    schuljahr_start = timezone.make_aware(schuljahr_start)
    schuljahr_ende = timezone.make_aware(schuljahr_ende)

    classes = SchoolClass.objects.annotate(
        total_uploads=Count(
            'posts',
            filter=Q(posts__uploaded_at__range=(schuljahr_start, schuljahr_ende)),
            distinct=True
        ),
        total_likes=Count(
            'posts__likes',
            filter=Q(posts__uploaded_at__range=(schuljahr_start, schuljahr_ende)),
            distinct=True
        ),
        total_uses=Count(
            'posts',
            filter=Q(posts__is_used=True) & Q(posts__uploaded_at__range=(schuljahr_start, schuljahr_ende)),
            distinct=True
        )
    ).order_by(sort_field_class)
    
    

    return render(request, 'photonest/sites/dashboard.html', {
        'users': users,
        'classes': classes,
        'current_sort_user': sort_field_user,
        'current_sort_class': sort_field_class,
        'timestamp': now().timestamp(),
        'reported_post_count': Post.objects.filter(is_reported=True).count(),
    })

@login_required
def profile(request):    
    return render(request, 'photonest/sites/profile.html', {
        'timestamp': now().timestamp(),
        'reported_post_count': Post.objects.filter(is_reported=True).count(),
    })

@login_required
def settings(request):    
    return render(request, 'photonest/sites/settings.html', {
        'timestamp': now().timestamp(),
        'reported_post_count': Post.objects.filter(is_reported=True).count(),
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
        request.session['show_alert'] = True
        request.session['alert_message'] = "Post wurde erstellt!"
        request.session['alert_icon'] = "check"
        request.session['alert_type'] = "success"
    else:
        request.session['show_alert'] = True
        request.session['alert_message'] = "Hochladen Fehlgeschlagen"
        request.session['alert_icon'] = "xmark"
        request.session['alert_type'] = "error"
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

        request.session['show_alert'] = True
        request.session['alert_message'] = "Post wurde gelöscht!"
        request.session['alert_icon'] = "trash"
        request.session['alert_type'] = "error"
    else:
        request.session['show_alert'] = True
        request.session['alert_message'] = "Löschen Fehlgeschlagen!"
        request.session['alert_icon'] = "xmark"
        request.session['alert_type'] = "error"

    return redirect(request.POST.get('next', 'home'))

@login_required
@require_POST
def report_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = ReportForm(request.POST, request.FILES)
    if form.is_valid():
        reason = form.cleaned_data['reason']
        reason += f" (Foto/Video Nr. {request.POST.get('page_number', 'undefined')})"
        post.report(user=request.user, reported_for=reason)

        request.session['show_alert'] = True
        request.session['alert_message'] = "Post wurde gemeldet!"
        request.session['alert_icon'] = "flag"
        request.session['alert_type'] = "warning"
    else:
        request.session['show_alert'] = True
        request.session['alert_message'] = "Melden Fehlgeschlagen!"
        request.session['alert_icon'] = "xmark"
        request.session['alert_type'] = "error"
    return redirect(request.POST.get('next', 'home'))


@login_required
@permission_required('photonest.favor_post')
def release_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if(post.is_reported == False):
        return redirect('/gallery?only_reported=on')

    post.release()

    request.session['show_alert'] = True
    request.session['alert_message'] = "Post wurde wieder freigegeben!"
    request.session['alert_icon'] = "check"
    request.session['alert_type'] = "success"

    if(Post.objects.filter(is_reported=True).count() > 0): 
        return redirect('/gallery?only_reported=on')
    else:
        return redirect('/gallery')

@login_required
@permission_required('photonest.favor_post')
def duplicate_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.duplicate()

    request.session['show_alert'] = True
    request.session['alert_message'] = "Post wurde dupliziert!"
    request.session['alert_icon'] = "check"
    request.session['alert_type'] = "success"

    return redirect('/gallery')

@login_required
@permission_required('photonest.favor_post')
def post_versions(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    content_type = ContentType.objects.get_for_model(Post)
    versions = LogEntry.objects.filter(
        content_type=content_type,
        object_id=post.id
    ).order_by('-timestamp')

    def resolve_value(field, value):
        if value in [None, "", "null"]:
            return "-"
        try:
            if field == "user":
                user = User.objects.get(pk=value)
                return user.get_full_name() or user.username
            elif field == "school_class":
                return str(SchoolClass.objects.get(pk=value))
        except Exception:
            return value
        return value

    for version in versions:
        resolved_changes = {}
        for field, change in version.changes_dict.items():
            if isinstance(change, (list, tuple)) and len(change) == 2:
                old, new = change
                resolved_changes[field] = (
                    resolve_value(field, old),
                    resolve_value(field, new)
                )
            else:
                resolved_changes[field] = change
        version.changes = resolved_changes

    return render(request, 'photonest/sites/view_post_versions.html', {
        'post': post,
        'versions': versions,
        'timestamp': now().timestamp(),
        'reported_post_count': Post.objects.filter(is_reported=True).count(),
        'show_alert': request.session.pop('show_alert', False),
        'alert_message': request.session.pop('alert_message', ""),
        'alert_icon': request.session.pop('alert_icon', ""),
        'alert_type': request.session.pop('alert_type', ""),
    })

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.user and not request.user.is_superuser:
        return redirect('view_post', post_id=post.id)
    
    if request.method == 'POST':
        form = PostEditForm(
            request.POST, 
            request.FILES, 
            instance=post, 
            user=request.user
        )
        if form.is_valid():
            form.save()
            request.session['show_alert'] = True
            request.session['alert_message'] = "Post wurde bearbeitet!"
            request.session['alert_icon'] = "check"
            request.session['alert_type'] = "success"
            return redirect('view_post', post_id=post.id)
        else:
            request.session['show_alert'] = True
            request.session['alert_message'] = "Post bearbeiten fehlgeschlagen!"
            request.session['alert_icon'] = "error"
            request.session['alert_type'] = "xmark"
    else:
        form = PostEditForm(instance=post, user=request.user)

    max_new_files = 5 - post.media_files.count()
    
    return render(request, 'photonest/sites/edit_post.html', {
        'form': form,
        'post': post,
        'max_new_files': max_new_files,
        'timestamp': now().timestamp(),
        'reported_post_count': Post.objects.filter(is_reported=True).count(),
        'show_alert': request.session.pop('show_alert', False),
        'alert_message': request.session.pop('alert_message', ""),
        'alert_icon': request.session.pop('alert_icon', ""),
        'alert_type': request.session.pop('alert_type', ""),
    })

@login_required
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'photonest/sites/view_post_detail.html', {
        'post': post,
        'timestamp': now().timestamp(),
        'report_form': ReportForm(),
        'reported_post_count': Post.objects.filter(is_reported=True).count(),
        'pageprefix': 'detail',
        'show_alert': request.session.pop('show_alert', False),
        'alert_message': request.session.pop('alert_message', ""),
        'alert_icon': request.session.pop('alert_icon', ""),
        'alert_type': request.session.pop('alert_type', ""),
    })

@login_required
def download_all_post_media(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    media_files = post.media_files.all()

    info_text = f"Post ID: {post.id}\n"
    info_text += f"User: {post.user.username}\n"
    info_text += f"Beschreibung: {post.description}\n"
    info_text += f"Anzahl Medien: {media_files.count()}\n"
    info_text += f"Klasse: {post.school_class.class_name}\n"
    info_text += f"Erstellt am: {post.uploaded_at.strftime('%d.%m.%Y %H:%M')}\n"
    info_text += f"Likes: {post.likes.count()} (Stand: {timezone.now().strftime('%d.%m.%Y %H:%M')}\n"
    info_text += f"Favoriten: {post.favorites.count()} (Stand: {timezone.now().strftime('%d.%m.%Y %H:%M')}\n"

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for media in media_files:
            file_path = media.media_file.path
            zipf.write(file_path, os.path.basename(file_path))
        
        zipf.writestr('info.txt', info_text)

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="post_{post_id}_media.zip"'

    post.mark_as_used(used_in="download", used_from=request.user)
    return response

@login_required
def download_single_media(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    file_path = media.media_file.path

    related_posts = media.posts.all()
    for post in related_posts:
        post.mark_as_used(used_in="download", used_from=request.user)
    return FileResponse(open(file_path, 'rb'), as_attachment=True)

@login_required
def delete_media(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    if request.user == media.posts.first().user or request.user.is_superuser:
        post = media.posts.first()

        if media.posts.count() == 1:
            media.media_file.delete(save=False)
        media.delete()

    next_url = request.POST.get('next', '')
    if next_url:
        return redirect(next_url)
    elif post:
        return redirect('edit_post', post_id=post.id)
    return redirect('gallery')