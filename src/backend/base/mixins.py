from rest_framework import mixins


class FarmersHeavenCreateModelMixin(mixins.CreateModelMixin):
    """
    Create a model instance.
    """
    def perform_create(self, serializer, *args, **kwargs):
        return serializer.save(*args, **kwargs)


class FarmersHeavenUpdateModelMixin(mixins.UpdateModelMixin):
    """
    Update a model instance.
    """
    def perform_update(self, serializer, *args, **kwargs):
        return serializer.save(*args, **kwargs)
