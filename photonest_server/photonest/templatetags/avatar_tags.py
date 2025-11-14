from django import template

register = template.Library()

@register.filter
def user_initials(username: str):
    if not username:
        return ""

    username = username.strip()

    # Wenn ein Punkt existiert
    if "." in username:
        parts = username.split(".")
        if len(parts[0]) > 0 and len(parts[1]) > 0:
            return (parts[0][0] + parts[1][0]).upper()

    # Wenn kein Punkt -> erste 2 Buchstaben
    cleaned = username.replace(" ", "")
    if len(cleaned) >= 2:
        return cleaned[:2].upper()

    # Fallback wenn der Name nur 1 Zeichen hat
    return cleaned.upper()
