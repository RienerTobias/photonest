from django import template
register = template.Library()

@register.filter
def has_liked(post, user):
    return post.likes.filter(id=user.id).exists() if user.is_authenticated else False