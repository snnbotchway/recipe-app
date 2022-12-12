"""Tag API tests."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipe.models import Tag
from recipe.serializers import TagSerializer

from rest_framework import status
from rest_framework.test import APIClient


TAGS_URL = reverse('recipe:tag-list')


def tag_detail_url(tag_id):
    """Return a tag detail URL."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_tag(user, **params):
    """Creates and returns new tag"""
    defaults = {
        "name": "Sample Tag",
    }
    defaults.update(params)
    return Tag.objects.create(user=user, **defaults)


class PublicTagAPITests(TestCase):
    """Test public features of the tag API."""

    def setUp(self):
        """Setup unauthenticated client."""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testPass123')

    def test_if_anonymous_user_create_tag_returns_401(self):
        """Test anonymous user cannot create tag."""
        payload = {"name": "Sample Tag"}

        response = self.client.post(TAGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Tag.objects.all().exists())

    def test_if_anonymous_user_get_tags_returns_401(self):
        """Test that anonymous user cannot get tags."""

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(response.data["detail"])

    def test_update_tag_if_user_is_anonymous_returns_401(self):
        """Test anonymous user cannot update given tag"""
        tag = create_tag(user=self.user)
        payload = {"name": "New tag name"}

        response = self.client.patch(
            tag_detail_url(tag.id), payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Tag.objects.filter(
            name=payload["name"]).exists())

    def test_delete_tag_if_user_is_anonymous_returns_401(self):
        """Test anonymous user cannot delete given tag"""
        tag = create_tag(user=self.user)

        response = self.client.delete(tag_detail_url(tag.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Tag.objects.filter(id=tag.id).exists())


class PrivateTagAPITests(TestCase):
    """Test features of the tag API which require authentication."""

    def setUp(self):
        """
        Authenticate client with user1 for further tests.
        User2 will be an anonymous user.
        """
        self.client = APIClient()
        self.user1 = get_user_model().objects.create_user(
            email='test1@example.com',
            password='testPass123')
        self.user2 = get_user_model().objects.create_user(
            email='test2@example.com',
            password='testPass123')
        self.client.force_authenticate(user=self.user1)

    def test_tag_list_is_limited_to_user_and_returns_200(self):
        """Test that authenticated user can get only his/her tags."""
        create_tag(user=self.user1)
        create_tag(user=self.user2)

        response = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(user=self.user1).order_by('-id')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for index in range(len(response.data)):
            self.assertDictContainsSubset(
                serializer.data[index], response.data[index])

    def test_user_create_tag_with_invalid_data_returns_400(self):
        """Test authenticated user cannot create tag with invalid data"""
        payload = {"name": ""}

        response = self.client.post(TAGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data["name"])

    def test_user_create_tag_with_valid_data_returns_201(self):
        """Test authenticated user can create tag with valid data"""
        payload = {"name": "Tag name"}

        response = self.client.post(TAGS_URL, payload)

        tag = Tag.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tag.name, payload["name"])
        self.assertEqual(tag.user, self.user1)

    def test_get_tag_detail_if_exists_returns_200(self):
        """Test get tag detail if exists successful"""
        tag = create_tag(user=self.user1)

        response = self.client.get(tag_detail_url(tag.id))

        serializer = TagSerializer(tag)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictContainsSubset(serializer.data, response.data)

    def test_get_tag_detail_if_not_exists_returns_404(self):
        """Test get tag which doesn't exist returns error 404"""
        tag = create_tag(user=self.user1)

        response = self.client.get(tag_detail_url(tag.id+1))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(response.data["detail"])
        self.assertFalse(response.data.get("id"))

    def test_get_other_user_tag_detail_returns_404(self):
        """Test get tag which doesn't belong to you returns error 404"""
        tag = create_tag(user=self.user2)

        response = self.client.get(tag_detail_url(tag.id))

        self.assertTrue(response.data["detail"])
        self.assertFalse(response.data.get("id"))

    def test_partial_update_tag_returns_200(self):
        """Test authenticated user can edit given tag"""
        original_name = "Original Name"
        tag = create_tag(user=self.user1, name=original_name)
        payload = {"name": "New name"}

        response = self.client.patch(
            tag_detail_url(tag.id), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])
        self.assertEqual(tag.user, self.user1)

    def test_full_update_tag_returns_200(self):
        """Test authenticated user can replace given tag"""
        tag = create_tag(user=self.user1)
        payload = {"name": "New name"}

        response = self.client.put(
            tag_detail_url(tag.id), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])
        self.assertEqual(tag.user, self.user1)

    def test_cannot_update_tag_user(self):
        """Test changing the tag's user is not possible."""
        tag = create_tag(user=self.user1)

        payload = {"user": self.user2.id}
        self.client.patch(
            tag_detail_url(tag.id), payload)

        tag.refresh_from_db()
        self.assertEqual(tag.user, self.user1)

    def test_update_other_user_tag_returns_404(self):
        """Test authenticated user cannot update another user's tag"""
        tag = create_tag(user=self.user2)
        payload = {"name": "New name"}

        response = self.client.patch(
            tag_detail_url(tag.id), payload)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(response.data["detail"])
        tag.refresh_from_db()
        self.assertNotEqual(tag.name, payload["name"])
        self.assertEqual(tag.user, self.user2)

    def test_delete_tag_returns_204(self):
        """Test authenticated user can delete a tag"""
        tag = create_tag(user=self.user1)

        response = self.client.delete(tag_detail_url(tag.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_delete_other_user_tag_returns_404(self):
        """Test authenticated user cannot delete another user's tag"""
        tag = create_tag(user=self.user2)

        response = self.client.delete(tag_detail_url(tag.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(response.data["detail"])
        self.assertTrue(Tag.objects.filter(id=tag.id).exists())
