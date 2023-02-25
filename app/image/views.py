from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from image.helpers import (
    convert_to_bytes,
    get_expiry_date,
    get_user,
    link_not_expired,
    user_exists,
)
from image.models import Image, Link, Plan, Subscriber
from image.serializers import PlanSerializer, SubscriberSerializer, UserSerializer
from PIL import Image as image_processor
from rest_framework import permissions, viewsets


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
    custom_size = list(map(int, [request.POST.get("x", 0), request.POST.get("y", 0)]))

    image = Image.objects.create(image=request.FILES["image"], author=user)
    links = generate_links(image, request.get_host(), expires_in, custom_size)

    return JsonResponse(links)


@link_not_expired
def serve_original_image(request, image_id):
    image = get_object_or_404(Image, pk=image_id)
    return HttpResponse(
        convert_to_bytes(image_processor.open(image.image._get_file())),
        content_type="image/jpeg",
    )


@link_not_expired
def fetch_thumbnails(request):
    link = Link.objects.get(url=request.path)
    resized_image = cache.get(link.resized_image)
    if resized_image is None:
        handle_cache_miss(link)
        cache.get(link.resized_image)
    return HttpResponse(resized_image, content_type="image/jpeg")


def handle_cache_miss(link):
    image = Image.objects.get(id=link.image_id)
    x, y = list(map(int, link.resized_image.rsplit("-", 1)[1].split("x")))
    resize_and_save(image, x, y)


def generate_links(image, host, expires_in, custom_size):
    plan_details = User.objects.get(username=image.author).subscriber.plan
    expiry = plan_details.expiring_links
    original_image = plan_details.original_image
    expiry_date = get_expiry_date(expires_in)
    thumbnail_sizes = [] + plan_details.thumbnail_sizes
    if any(custom_size):
        thumbnail_sizes = thumbnail_sizes + [custom_size]

    links = {}
    for x, y in thumbnail_sizes:
        url = reverse("fetch_thumbnails", args=(x, y, image.id))
        links[f"{x}x{y}"] = f"{host}{url}"
        Link.objects.create(
            url=url,
            image=image,
            resized_image=f"{image.id}-{x}x{y}",
            expires=expiry,
            expiry_date=expiry_date,
        )

        resize_and_save(image, x, y)

    if original_image:
        url = reverse("serve_original_image", args=(image.id,))
        Link.objects.create(
            url=url, image=image, expires=expiry, expiry_date=expiry_date
        )
        links["original"] = f"{host}{url}"

    return links


def resize_and_save(image, x, y):
    image_object = image_processor.open(image.image._get_file())
    _x, _y = x, y  # _x and _y are used as ids for the link; so cannot change
    if x == 0:
        x = int(image_object.width * (y / image_object.height))
    if y == 0:
        y = int((x / image_object.width) * image_object.height)

    resized = image_object.resize((x, y))
    cache.set(f"{image.id}-{_x}x{_y}", convert_to_bytes(resized))


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
