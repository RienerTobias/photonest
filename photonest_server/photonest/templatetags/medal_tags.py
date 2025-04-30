from django.conf import settings
from django import template
from django.utils.safestring import mark_safe
from django.db.models import Count, Q

register = template.Library()

@register.filter
def get_medal_icons(queryset):
    medals = ""
    user = queryset

    bronze = "#ce8946"
    silver = "#c0c0c0"
    gold = "#ffd700"

    likeIcon = "heart"
    uploadsIcon = "upload"
    usesIcon = "bullseye-arrow"

    def medal(color, icon):
        return f'<span class="badge badge-sm m-1"><i class="fa-duotone fa-solid fa-medal" style="--fa-primary-color: {color}; --fa-secondary-color: {color};"></i><i class="fa-solid fa-{icon}"></i></span>'

    if(user.likes_received >= settings.GOLD_MEDAL_LIMIT):
        medals += medal(gold, likeIcon)
    elif(user.likes_received >= settings.SILVER_MEDAL_LIMIT):
        medals += medal(silver, likeIcon)
    elif(user.likes_received >= settings.BRONZE_MEDAL_LIMIT):
        medals += medal(bronze, likeIcon)

    if(user.uploads_count >= settings.GOLD_MEDAL_LIMIT):
        medals += medal(gold, uploadsIcon)
    elif(user.uploads_count >= settings.SILVER_MEDAL_LIMIT):
        medals += medal(silver, uploadsIcon)
    elif(user.uploads_count >= settings.BRONZE_MEDAL_LIMIT):
        medals += medal(bronze, uploadsIcon)
    
    if(user.uses_count >= settings.GOLD_MEDAL_LIMIT):
        medals += medal(gold, usesIcon)
    elif(user.uses_count >= settings.SILVER_MEDAL_LIMIT):
        medals += medal(silver, usesIcon)
    elif(user.uses_count >= settings.BRONZE_MEDAL_LIMIT):
        medals += medal(bronze, usesIcon)

    try:
        return mark_safe(medals)
    except IndexError:
        return None

@register.filter
def has_medal(queryset, args):
    user = queryset

    try:
        medal_type, medal_tier = args.split(',')
        medal_type = medal_type.strip().lower()
        medal_tier = medal_tier.strip().upper()
    except ValueError:
        return False

    counts = {
        'uploads': user.posts.count(),   
        'likes': user.posts.aggregate(total_likes=Count('likes'))['total_likes'],         
        'uses': user.posts.filter(is_used=True).count(),           
    }

    setting_name = f"{medal_tier}_MEDAL_LIMIT"
    required = getattr(settings, setting_name, None)

    if not required or medal_type not in counts:
        return False

    return counts[medal_type] >= required

@register.simple_tag
def bronze_count():
    return settings.BRONZE_MEDAL_LIMIT

@register.simple_tag
def silver_count():
    return settings.SILVER_MEDAL_LIMIT

@register.simple_tag
def gold_count():
    return settings.GOLD_MEDAL_LIMIT