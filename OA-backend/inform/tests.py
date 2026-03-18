from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from oaauth.models import OAUser, OADepartment, UserStatusChoices
from inform.models import Inform, InformRead
import datetime


class InformModelTests(TestCase):
    """Test Inform and InformRead models"""

    def setUp(self):
        self.department = OADepartment.objects.create(
            name="Test Department",
            intro="Test Department Introduction"
        )
        self.user = OAUser.objects.create_user(
            realname="Test User",
            email="test@example.com",
            password="testpass123",
            status=UserStatusChoices.ACTIVED,
            department=self.department
        )
        self.another_user = OAUser.objects.create_user(
            realname="Another User",
            email="another@example.com",
            password="testpass456",
            status=UserStatusChoices.ACTIVED,
            department=self.department
        )

        self.inform_public = Inform.objects.create(
            title="Public Notification",
            content="This is a public notification",
            public=True,
            author=self.user
        )
        self.inform_private = Inform.objects.create(
            title="Department Notification",
            content="This is a department notification",
            public=False,
            author=self.user
        )
        self.inform_private.departments.add(self.department)

    def test_inform_creation(self):
        self.assertEqual(self.inform_public.title, "Public Notification")
        self.assertEqual(self.inform_public.content, "This is a public notification")
        self.assertTrue(self.inform_public.public)
        self.assertEqual(self.inform_public.author, self.user)
        self.assertEqual(self.inform_public.departments.count(), 0)

        self.assertEqual(self.inform_private.title, "Department Notification")
        self.assertFalse(self.inform_private.public)
        self.assertEqual(self.inform_private.departments.count(), 1)
        self.assertEqual(self.inform_private.departments.first(), self.department)

    def test_inform_read_creation(self):
        read_record = InformRead.objects.create(
            inform=self.inform_public,
            user=self.user
        )
        self.assertEqual(read_record.inform, self.inform_public)
        self.assertEqual(read_record.user, self.user)
        self.assertIsInstance(read_record.read_time, datetime.datetime)

        with self.assertRaises(Exception):
            InformRead.objects.create(
                inform=self.inform_public,
                user=self.user
            )

    def test_inform_meta_ordering(self):
        inform1 = Inform.objects.create(
            title="Notification 1",
            content="Content 1",
            public=True,
            author=self.user
        )
        inform2 = Inform.objects.create(
            title="Notification 2",
            content="Content 2",
            public=True,
            author=self.user
        )
        informs = Inform.objects.all()
        self.assertEqual(informs[0], inform2)
        self.assertEqual(informs[1], inform1)


class InformViewSetTests(TestCase):
    """Test InformViewSet with JWT authentication"""

    def setUp(self):
        self.client = APIClient()
        self.department = OADepartment.objects.create(
            name="Test Department",
            intro="Test Department Introduction"
        )
        self.user = OAUser.objects.create_user(
            realname="Test User",
            email="test@example.com",
            password="testpass123",
            status=UserStatusChoices.ACTIVED,
            department=self.department
        )
        self.another_user = OAUser.objects.create_user(
            realname="Another User",
            email="another@example.com",
            password="testpass456",
            status=UserStatusChoices.ACTIVED,
            department=self.department
        )

        # Login to get JWT token
        login_url = reverse("oaauth:login")
        login_data = {"email": "test@example.com", "password": "testpass123"}
        login_resp = self.client.post(login_url, login_data, format="json")
        self.token = login_resp.json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {self.token}')

        # Create test data (only 3 visible to current user)
        self.public_inform = Inform.objects.create(
            title="Public Notification",
            content="Public content",
            public=True,
            author=self.user
        )
        self.department_inform = Inform.objects.create(
            title="Department Notification",
            content="Department content",
            public=False,
            author=self.another_user
        )
        self.department_inform.departments.add(self.department)
        self.private_inform = Inform.objects.create(
            title="Personal Notification",
            content="Personal content",
            public=False,
            author=self.user
        )
        

    def test_get_queryset(self):
        url = reverse('inform:inform-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 4)

        # Switch to another user
        login_url = reverse("oaauth:login")
        login_data = {"email": "another@example.com", "password": "testpass456"}
        login_resp = self.client.post(login_url, login_data, format="json")
        token = login_resp.json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')

        response = self.client.get(url)
        self.assertEqual(len(response.json()), 4)  

    def test_retrieve_inform(self):
        url = reverse('inform:inform-detail', kwargs={'pk': self.public_inform.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['title'], "Public Notification")
        self.assertIn('read_count', data)
        self.assertEqual(data['read_count'], 0)

        InformRead.objects.create(inform=self.public_inform, user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.json()['read_count'], 1)

    def test_destroy_inform(self):
        # Can delete own notification
        url = reverse('inform:inform-detail', kwargs={'pk': self.public_inform.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Cannot delete others' notification (returns 401 Unauthorized)
        url = reverse('inform:inform-detail', kwargs={'pk': self.department_inform.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReadInformViewTests(TestCase):
    """Test ReadInformView with JWT authentication"""

    def setUp(self):
        self.client = APIClient()
        self.department = OADepartment.objects.create(
            name="Test Department",
            intro="Test Department Introduction"
        )
        self.user = OAUser.objects.create_user(
            realname="Test User",
            email="test@example.com",
            password="testpass123",
            status=UserStatusChoices.ACTIVED,
            department=self.department
        )

        # Login to get JWT token
        login_url = reverse("oaauth:login")
        login_data = {"email": "test@example.com", "password": "testpass123"}
        login_resp = self.client.post(login_url, login_data, format="json")
        self.token = login_resp.json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {self.token}')

        self.inform = Inform.objects.create(
            title="Test Notification",
            content="Test content",
            public=True,
            author=self.user
        )

    def test_mark_inform_as_read(self):
        url = reverse('inform:read_inform')
        data = {"inform_pk": self.inform.id}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(InformRead.objects.count(), 1)
        self.assertTrue(InformRead.objects.filter(
            inform=self.inform,
            user=self.user
        ).exists())

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(InformRead.objects.count(), 1)

        data = {"inform_pk": 9999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_inform_serializer_validation(self):
        url = reverse('inform:read_inform')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], 'Please provide the ID of the inform!')

        response = self.client.post(url, {"inform_pk": "invalid"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)