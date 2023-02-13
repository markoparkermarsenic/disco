import uuid

from django.contrib.auth.models import User
from django.db import models
from image.validators import validate_expiry, validate_thumbnail_sizes

# Create your models here.


class Plan(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    thumbnail_sizes = models.JSONField(validators=[validate_thumbnail_sizes])
    expiring_links = models.BooleanField()
    original_image = models.BooleanField()

    def __str__(self):
        return f"Name: {self.name}, Thumbnail Sizes: {self.thumbnail_sizes}, Expiring Links: {self.expiring_links}, Can see Original image: {self.original_image}"


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to="images/")
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"uuid: {self.id}, Author: {self.author}"


class Link(models.Model):
    url = models.URLField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    expires = models.BooleanField()
    expiry_date = models.DateTimeField(
        null=True, blank=True, default=None, validators=[validate_expiry]
    )
    resized_image = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return f"Link: {self.url}"


class Subscriber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    def __str__(self):
        return f"User: {self.user}, Plan: {self.plan}"
