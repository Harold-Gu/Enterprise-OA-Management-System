# staff/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from oaauth.models import OADepartment, UserStatusChoices
from utils import aeser
from django.conf import settings
import json
import pandas as pd
from io import BytesIO

OAUser = get_user_model()
aes = aeser.AESCipher(settings.SECRET_KEY)


class StaffTestCase(TestCase):
    """Unit tests for staff management module"""

    def setUp(self):
        """Initialize test data and authenticate test user with JWT"""
        self.board_dept = OADepartment.objects.create(
            name="Board Department",
            intro="Board Department Introduction"
        )
        self.normal_dept = OADepartment.objects.create(
            name="Tech Department",
            intro="Tech Department Introduction"
        )

        self.board_user = OAUser.objects.create_user(
            email="board@test.com",
            realname="Board Member",
            password="123456",
            status=UserStatusChoices.ACTIVED,
            department=self.board_dept
        )
        self.board_dept.leader = self.board_user
        self.board_dept.save()

        self.dept_leader = OAUser.objects.create_user(
            email="leader@test.com",
            realname="Tech Department Leader",
            password="123456",
            status=UserStatusChoices.ACTIVED,
            department=self.normal_dept
        )
        self.normal_dept.leader = self.dept_leader
        self.normal_dept.save()

        self.normal_user = OAUser.objects.create_user(
            email="normal@test.com",
            realname="Normal Staff",
            password="123456",
            status=UserStatusChoices.ACTIVED,
            department=self.normal_dept
        )

        self.client = APIClient()
        self._authenticate_user(self.board_user)

    def _authenticate_user(self, user):
        """Helper method to authenticate a user with JWT token"""
        login_url = reverse("oaauth:login")
        login_data = {
            "email": user.email,
            "password": "123456"
        }
        login_resp = self.client.post(login_url, login_data, format="json")
        token = login_resp.json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')

    def test_add_staff_permission(self):
        """Test permission control for adding new staff"""
        self._authenticate_user(self.normal_user)
        add_data = {
            "realname": "Test Staff",
            "email": "test1@test.com",
            "password": "123456",
            "department_id": self.normal_dept.pk
        }
        response = self.client.post(reverse("staff:staff-list"), add_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Non-department leaders are not allowed to add employees!")

        self._authenticate_user(self.dept_leader)
        add_data["email"] = "test2@test.com"
        response = self.client.post(reverse("staff:staff-list"), add_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = OAUser.objects.get(email="test2@test.com")
        self.assertEqual(user.department, self.normal_dept)
        self.assertEqual(user.status, UserStatusChoices.UNACTIVE)

        self._authenticate_user(self.board_user)
        add_data["email"] = "test3@test.com"
        add_data["department_id"] = self.normal_dept.pk
        response = self.client.post(reverse("staff:staff-list"), add_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = OAUser.objects.get(email="test3@test.com")
        self.assertEqual(user.department, self.normal_dept)

    def test_staff_list_filter(self):
        """Test staff list filtering and permission control"""
        self._authenticate_user(self.board_user)
        response = self.client.get(f"{reverse('staff:staff-list')}?department_id={self.normal_dept.pk}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.json()["results"]:
            self.assertEqual(item["department"]["id"], self.normal_dept.pk)

        self._authenticate_user(self.dept_leader)
        response = self.client.get(reverse("staff:staff-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.json()["results"]:
            self.assertEqual(item["department"]["id"], self.normal_dept.pk)

        self._authenticate_user(self.normal_user)
        response = self.client.get(reverse("staff:staff-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_upload(self):
        """Test bulk staff upload functionality"""
        self._authenticate_user(self.normal_user)
        empty_file = BytesIO()
        response = self.client.post(
            reverse("staff:upload_staff"),
            {"file": empty_file},
            format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self._authenticate_user(self.board_user)
        output = BytesIO()
        df = pd.DataFrame({
            "name": ["Batch Staff 1", "Batch Staff 2"],
            "email": ["batch1@test.com", "batch2@test.com"],
            "department": ["Tech Department"] * 2
        })
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        response = self.client.post(
            reverse("staff:upload_staff"),
            {"file": output},
            format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_download(self):
        """Test staff information download functionality"""
        self._authenticate_user(self.normal_user)
        pks = json.dumps([self.normal_user.pk])
        response = self.client.get(f"{reverse('staff:download_staff')}?pks={pks}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self._authenticate_user(self.dept_leader)
        pks = json.dumps([self.normal_user.pk, self.dept_leader.pk])
        response = self.client.get(f"{reverse('staff:download_staff')}?pks={pks}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/xlsx")
        self.assertIn("staff's information.xlsx", response["Content-Disposition"])

        excel_data = pd.read_excel(BytesIO(response.content))
        self.assertEqual(len(excel_data), 2)