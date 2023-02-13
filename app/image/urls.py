from django.urls import path
from image.views import (fetch_thumbnails, list_images, serve_original_image,
                         upload_image)

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
]
