from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from oaauth.models import OAUser, OADepartment, UserStatusChoices
import jwt
import time
from django.conf import settings


class OAauthViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create a test department
        self.dept = OADepartment.objects.create(
            name="Test Department",
            intro="Test Intro"
        )
        
        # Create users in different status 
        # 1. normal user who is activated
        self.active_user = OAUser.objects.create_user(
            realname="Active User",
            email="active@test.com",
            password="123456",
            status=UserStatusChoices.ACTIVED,
            department=self.dept
        )
        
        # 2. unactive user
        self.unactive_user = OAUser.objects.create_user(
            realname="Unactive User",
            email="unactive@test.com",
            password="123456",
            status=UserStatusChoices.UNACTIVE,
            department=self.dept
        )
        
        # 3. locked user
        self.locked_user = OAUser.objects.create_user(
            realname="Locked User",
            email="locked@test.com",
            password="123456",
            status=UserStatusChoices.LOCKED,
            department=self.dept
        )
        
        # login
        self.login_url = reverse("oaauth:login")
        self.reset_pwd_url = reverse("oaauth:resetpwd")

    # ======================
    # Test1: normal login
    # ======================
    def test_login_success(self):
        data = {
            "email": "active@test.com",
            "password": "123456"
        }
        response = self.client.post(self.login_url, data, format="json")
        response_data = response.json()  
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify the token and the info
        self.assertIn("token", response_data)
        self.assertIn("user", response_data)
        self.assertEqual(response_data["user"]["email"], "active@test.com")
        # the last_login field is renewed
        self.active_user.refresh_from_db()
        self.assertIsNotNone(self.active_user.last_login)

    # not exist user login
    def test_login_user_not_exist(self):
        data = {
            "email": "notexist@test.com",
            "password": "123456"
        }
        response = self.client.post(self.login_url, data, format="json")
        response_data = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data["detail"], "User does not exist.")

    def test_login_wrong_password(self):
        # Wrong password
        data = {
            "email": "active@test.com",
            "password": "wrongpwd"
        }
        response = self.client.post(self.login_url, data, format="json")
        response_data = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data["detail"], "Incorrect password.")

    def test_login_unactive_user(self):
        # Unactive user login
        data = {
            "email": "unactive@test.com",
            "password": "123456"
        }
        response = self.client.post(self.login_url, data, format="json")
        response_data = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data["detail"], "This user is inactive.")

    def test_login_locked_user(self):
        # Locked user
        data = {
            "email": "locked@test.com",
            "password": "123456"
        }
        response = self.client.post(self.login_url, data, format="json")
        response_data = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data["detail"], "This user is locked.")

    # ======================
    # Test2: Reset the password
    # ======================
    def test_reset_pwd_success(self):
        # Reset password success
        # 1. login get the token
        login_data = {"email": "active@test.com", "password": "123456"}
        login_resp = self.client.post(self.login_url, login_data, format="json")
        login_resp_data = login_resp.json()
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {login_resp_data["token"]}')
        
        # 2. send request to reset the password
        reset_data = {
            "oldpwd": "123456",
            "pwd1": "654321",
            "pwd2": "654321"
        }
        response = self.client.post(self.reset_pwd_url, reset_data, format="json")
        
        # 3. verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. verify new password
        self.active_user.refresh_from_db()
        self.assertTrue(self.active_user.check_password("654321"))

    def test_reset_pwd_wrong_old_pwd(self):
        # reset password - old password is wrong
        # login
        login_data = {"email": "active@test.com", "password": "123456"}
        login_resp = self.client.post(self.login_url, login_data, format="json")
        login_resp_data = login_resp.json()
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {login_resp_data["token"]}')
        
        # send request with wrong old password
        reset_data = {
            "oldpwd": "wrongold",
            "pwd1": "654321",
            "pwd2": "654321"
        }
        response = self.client.post(self.reset_pwd_url, reset_data, format="json")
        response_data = response.json()
        
        # verify the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data["detail"], "Old password is incorrect!")
        
        # The password does not change 
        self.active_user.refresh_from_db()
        self.assertTrue(self.active_user.check_password("123456"))

    def test_reset_pwd_pwd_not_match(self):
        # Reset password - reenter new password wrongly
        # login
        login_data = {"email": "active@test.com", "password": "123456"}
        login_resp = self.client.post(self.login_url, login_data, format="json")
        login_resp_data = login_resp.json()
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {login_resp_data["token"]}')
        
        # Send request with two different new password
        reset_data = {
            "oldpwd": "123456",
            "pwd1": "654321",
            "pwd2": "123456"
        }
        response = self.client.post(self.reset_pwd_url, reset_data, format="json")
        response_data = response.json()
        
        # verify the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_data["detail"], "The two new passwords do not match!")
        
        # the password does not change
        self.active_user.refresh_from_db()
        self.assertTrue(self.active_user.check_password("123456"))

    def test_reset_pwd_without_auth(self):
        # reset password -- doesn't login 
        # send request without login
        reset_data = {
            "oldpwd": "123456",
            "pwd1": "654321",
            "pwd2": "654321"
        }
        response = self.client.post(self.reset_pwd_url, reset_data, format="json")
        response_data = response.json()  
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_data["detail"], "Please log in first!")

    def test_reset_pwd_invalid_token(self):
        # Incalid JWT
        # set invalid token
        self.client.credentials(HTTP_AUTHORIZATION='JWT invalid_token_123456')
        
        reset_data = {
            "oldpwd": "123456",
            "pwd1": "654321",
            "pwd2": "654321"
        }
        response = self.client.post(self.reset_pwd_url, reset_data, format="json")
        response_data = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_data["detail"], "Please log in first!")

    def test_reset_pwd_expired_token(self):
        # init expired token
        expire_time = time.time() - 3600  # expired for 1 hour
        expired_token = jwt.encode(
            {"userid": self.active_user.pk, "exp": expire_time},
            key=settings.SECRET_KEY,
            algorithm="HS256"  
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {expired_token}')
        
        reset_data = {
            "oldpwd": "123456",
            "pwd1": "654321",
            "pwd2": "654321"
        }
        response = self.client.post(self.reset_pwd_url, reset_data, format="json")
        response_data = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_data["detail"], "Please log in first!")