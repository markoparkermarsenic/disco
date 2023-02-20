from io import BytesIO

from django.http import HttpResponseForbidden
from django.utils import timezone
from image.models import Link, User


def link_not_expired(func):
    def wrapper(request, *args, **kwargs):
        link = Link.objects.get(url=request.path)
        if link.expiry_date and link.expiry_date <= timezone.now():
            # Link has expired
            return HttpResponseForbidden("Link Expired")
        return func(request, *args, **kwargs)

    return wrapper


def convert_to_bytes(image, format="JPEG"):
    buf = BytesIO()
    image.save(buf, format=format)
    return buf.getvalue()


def user_exists(func):
    def wrapper(request, *args, **kwargs):
        if request.method == "POST":
            user = get_user(request.POST.get("user"))
        if request.method == "GET":
            user = kwargs.get("username")
        if user is None:
            return HttpResponseForbidden("Invalid User")
        return func(request, *args, **kwargs)

    return wrapper


def get_user(user):
    try:
        return User.objects.get(username=user)
    except User.DoesNotExist:
        return None
