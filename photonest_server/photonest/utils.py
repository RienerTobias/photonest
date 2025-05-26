def duplicate_instance(instance, exclude_fields=None):
    exclude_fields = exclude_fields or []
    data = {
        field.name: getattr(instance, field.name)
        for field in instance._meta.fields
        if field.name not in exclude_fields and not field.auto_created and not field.primary_key
    }
    new_instance = instance.__class__.objects.create(**data)
    return new_instance