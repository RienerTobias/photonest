from django.conf import settings
from django import template
from django.utils.safestring import mark_safe

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