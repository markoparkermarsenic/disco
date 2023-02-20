from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from image.helpers import convert_to_bytes, get_user, link_not_expired, user_exists
from image.models import Image, Link
from PIL import Image as image_processor

from rest_framework import permissions
from image.models import Subscriber, Plan
from image.serializers import SubscriberSerializer, PlanSerializer, UserSerializer
from rest_framework import viewsets


@csrf_exempt
@user_exists
def upload_image(request):
    if request.method != "POST":
        return HttpResponse.HttpResponseNotAllowed(["POST"])

    user = get_user(request.POST.get("user"))
    expires_in = (
        None
        if request.POST.get("expires_in") is None
        else int(request.POST.get("expires_in"))
    )
    if expires_in is not None and not (300 <= int(expires_in) <= 3000):
        return HttpResponseBadRequest("expiry must be between 300-3000")

    image = Image.objects.create(image=request.FILES["image"], author=user)

    links = generate_links(image, request.get_host(), expires_in)

    return JsonResponse(links)


@link_not_expired
def serve_original_image(request, image_id):
    image = get_object_or_404(Image, pk=image_id)
    return HttpResponse(
        convert_to_bytes(image_processor.open(image.image._get_file())),
        content_type="image/jpeg",
    )


@link_not_expired
def fetch_thumbnails(request, width, height, image_id):
    link = Link.objects.get(url=request.path)
    resized_image = cache.get(link.resized_image)
    return HttpResponse(resized_image, content_type="image/jpeg")


def generate_links(image, host, expires_in):
    plan_details = User.objects.get(username=image.author).subscriber.plan
    expiry = plan_details.expiring_links
    original_image = plan_details.original_image
    expiry_date = get_expiry_date(expires_in)

    links = {}
    for x, y in plan_details.thumbnail_sizes:
        url = reverse("fetch_thumbnails", args=(x, y, image.id))
        links[f"{x}x{y}"] = f"{host}{url}"
        Link.objects.create(
            url=url,
            image=image,
            resized_image=f"{image.id}-{x}x{y}",
            expires=expiry,
            expiry_date=expiry_date,
        )

        resized = image_processor.open(image.image._get_file()).resize((x, y))
        cache.set(f"{image.id}-{x}x{y}", convert_to_bytes(resized))

    if original_image:
        url = reverse("serve_original_image", args=(image.id,))
        Link.objects.create(
            url=url, image=image, expires=expiry, expiry_date=expiry_date
        )
        links["original"] = f"{host}{url}"

    return links


@user_exists
def list_images(request, username):
    user = User.objects.get(username=username)
    owned_images = Image.objects.filter(author=user)
    image_info = {
        username: [
            {"id": str(i.id), "created": str(i.created.timestamp())}
            for i in owned_images
        ]
    }
    return JsonResponse(image_info)


def get_expiry_date(expires_in):
    if expires_in is None:
        return None
    return timezone.timedelta(seconds=expires_in) + timezone.now()


class PlanListCreateView(viewsets.ModelViewSet):
    """
    API endpoint that allows plans to be viewed or edited.
    """

    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAdminUser]


class SubscriberCreateView(viewsets.ModelViewSet):
    """
    API endpoint that allows Subscribers to be viewed or edited.
    """

    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer
    permission_classes = [permissions.IsAdminUser]


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
