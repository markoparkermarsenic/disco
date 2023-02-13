from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_thumbnail_sizes(entry):
    if not isinstance(entry, list):
        raise ValidationError("thumbnail_sizes must be a list of sizes")

    for thumbnail_size in entry:
        if not isinstance(thumbnail_size, list) or len(thumbnail_size) != 2:
            raise ValidationError("each thumbnail size must be a list of two integers")
        width, height = thumbnail_size
        if not isinstance(width, int) or not isinstance(height, int):
            raise ValidationError("width and height must be integers")
        if width <= 0 or height <= 0:
            raise ValidationError("width and height must be non 0 positive integers")


def validate_expiry(entry):
    if entry < timezone.now():
        raise ValidationError("Expiry cannot be in the past!")
