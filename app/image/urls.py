from django.urls import path, include
from rest_framework import routers

from image.views import (
    fetch_thumbnails,
    list_images,
    serve_original_image,
    upload_image,
    SubscriberCreateView,
    PlanListCreateView,
    UserViewSet
)


router = routers.DefaultRouter()
router.register(r"subscribers", SubscriberCreateView)
router.register(r"plans", PlanListCreateView)
router.register(r'users', UserViewSet)

urlpatterns = [
    path("upload/", upload_image, name="upload_image"),
    path("list_images/<str:username>", list_images, name="list_images"),
    path(
        "resized/<int:width>x<int:height>/<str:image_id>",
        fetch_thumbnails,
        name="fetch_thumbnails",
    ),
    path(
        "source_image/<str:image_id>", serve_original_image, name="serve_original_image"
    ),
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
