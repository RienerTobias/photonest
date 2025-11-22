from django import template
from django.conf import settings
from django.core.cache import cache
from PIL import Image, ImageOps
import os

register = template.Library()

@register.simple_tag
def compressed_image(media_file, width=800, format="webp", quality=70):
    """
    Komprimiert ein Bild und wendet EXIF-Orientation an, so dass Thumbnail
    dieselbe Orientierung wie das im Browser angezeigte Original hat.
    """
    format = format.lower()
    if format not in ("webp", "jpeg", "jpg"):
        raise ValueError("Format muss 'webp' oder 'jpeg' sein'")

    # Originalpfad bestimmen
    if hasattr(media_file, "path"):
        original_path = media_file.path
        url = media_file.url
    elif isinstance(media_file, str):
        url = media_file
        if url.startswith(settings.MEDIA_URL):
            relative = url[len(settings.MEDIA_URL):]
            original_path = os.path.join(settings.MEDIA_ROOT, relative)
        else:
            raise ValueError("Ungültiger media_file string")
    else:
        raise ValueError("media_file muss FileField oder URL sein")

    # Cache prüfen
    cache_key = f"thumb:{url}:{width}:{format}:{quality}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Zielpfad
    relative = url.replace(settings.MEDIA_URL, "")
    base, _ = os.path.splitext(relative)
    new_ext = ".webp" if format == "webp" else ".jpg"
    compressed_relative = f"{base}_{width}px{new_ext}"
    compressed_path = os.path.join(settings.MEDIA_ROOT, "compressed", compressed_relative)
    os.makedirs(os.path.dirname(compressed_path), exist_ok=True)

    try:
        img = Image.open(original_path)

        # --- EXIF-Orientation anwenden (Pixel rotieren) ---
        # exif_transpose dreht/flippt das Bild entsprechend EXIF-Orientation
        img = ImageOps.exif_transpose(img)

        # EXIF auslesen, Orientation (274) falls vorhanden auf 1 setzen
        exif = img.getexif()
        exif_bytes = None
        try:
            if exif and isinstance(exif, dict):
                # 274 ist das Tag für Orientation
                exif[274] = 1
                exif_bytes = exif.tobytes()
        except Exception:
            exif_bytes = None

        img = img.convert("RGB")

        # --- Orientierung nach Transpose prüfen und Thumbnail-Größe wählen ---
        orig_w, orig_h = img.size
        if orig_h > orig_w:
            # Hochformat: Höhe begrenzen
            # thumbnail nimmt max width/height — wir geben (max_w, max_h)
            target_size = (int(width * 0.6) if width==0 else width * 10000, width)
            # simpler: direkt (very large width, target height = width)
            target_size = (width * 10000, width)
        else:
            # Querformat: Breite begrenzen
            target_size = (width, width * 10000)

        img.thumbnail(target_size)

        # --- Speichern ---
        if format == "webp":
            # WebP: EXIF-Unterstützung ist je nach Pillow-Version eingeschränkt.
            # Hier speichern wir ohne EXIF (gängiges Verhalten).
            img.save(compressed_path, "WEBP", quality=quality, method=6)
        else:
            # JPEG: EXIF (bis auf Orientation) wieder mitspeichern, wenn möglich
            if exif_bytes:
                img.save(compressed_path, "JPEG", optimize=True, quality=quality, exif=exif_bytes)
            else:
                img.save(compressed_path, "JPEG", optimize=True, quality=quality)

    except Exception:
        # Bei Fehler fallback zum Original-URL
        return url

    compressed_url = settings.MEDIA_URL + "compressed/" + compressed_relative
    cache.set(cache_key, compressed_url, 60 * 60 * 24)
    return compressed_url
