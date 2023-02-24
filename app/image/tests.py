import json
from datetime import datetime, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from image.helpers import convert_to_bytes
from image.models import Image, Link, Plan, Subscriber
from PIL import Image as image_processor


# Create your tests here.
class UploadTest(TestCase):
    def setUp(self):
        basic = Plan.objects.create(
            name="Basic",
            thumbnail_sizes=[[200, 200]],
            expiring_links=True,
            original_image=False,
        )
        premium = Plan.objects.create(
            name="Premium",
            thumbnail_sizes=[[200, 200], [400, 400]],
            expiring_links=False,
            original_image=True,
        )
        enterprise = Plan.objects.create(
            name="Enterprise",
            thumbnail_sizes=[[200, 200], [400, 400]],
            expiring_links=True,
            original_image=True,
        )

        dev_user = User.objects.create(username="dev", password="mypass")
        subscriber = Subscriber.objects.create(user=dev_user, plan=enterprise)

        print("created test values!")

        image = image_processor.new("RGB", size=(50, 50), color=(155, 0, 0))
        image.save("test.jpg")

    def test_upload_image(self):
        response = self.post_image()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Image.objects.count(), 1)

    def test_valid_expiry(self):
        response = self.post_image(expires_in=301)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(Link.objects.count(), 3)

    def test_invalid_expiry(self):
        response = self.post_image(expires_in=299)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Image.objects.count(), 0)
        self.assertEqual(Link.objects.count(), 0)

    def test_upload_image_without_file(self):
        response = self.client.post(reverse("upload_image"), {})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Image.objects.count(), 0)

    def test_list_images(self):
        response = self.client.get(reverse("list_images", args=("dev",)))
        self.assertEqual(response.status_code, 200)

    def test_expired_image(self):
        response = self.post_image(expires_in=301)

        response_json = json.loads(response.content.decode())
        _, url = response_json["200x200"].split("testserver", 1)

        future = timezone.now() + timedelta(seconds=400)
        with patch("django.utils.timezone.now") as mock_timezone:
            mock_timezone.return_value = future
            response = self.client.get(url)

        self.assertEqual(response.content.decode(), "Link Expired")
        self.assertEqual(response.status_code, 403)

    def test_cache_miss(self):
        response = self.post_image(expires_in=301)

        response_json = json.loads(response.content.decode())
        _, url = response_json["200x200"].split("testserver", 1)

        with patch("django.core.cache.cache.get") as mock_cache:
            mock_cache.return_value = None
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def post_image(self, expires_in=301):
        image = image_processor.open("test.jpg")
        image = SimpleUploadedFile(
            "test_image.jpg", content=convert_to_bytes(image), content_type="image/jpeg"
        )
        response = self.client.post(
            reverse("upload_image"),
            {"image": image, "user": "dev", "expires_in": expires_in},
        )
        return response
