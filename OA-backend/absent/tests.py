from django.test import TestCase
from rest_framework import exceptions

from absent.models import Absent, AbsentType, AbsentStatusChoices
from oaauth.models import OAUser, OADepartment, UserStatusChoices
from absent.serializers import AbsentTypeSerializer, AbsentSerializer
from absent.utils import get_responder

# The core business logic of the test leave application model
class AbsentTest(TestCase):
    def setUp(self):
        # Init the test data

        # Create the departments
        self.dept_hr = OADepartment.objects.create(
            name="HR Department",
            leader=None,  
            manager=None
        )
        self.dept_other = OADepartment.objects.create(
            name="Other Department",
            leader=None,
            manager=None
        )

        # Create manager
        self.manager = OAUser.objects.create(
            realname="Boss", email="Boss@gmail.com", password="111111",
            status=UserStatusChoices.ACTIVED, is_superuser=True, department=self.dept_hr
        )

        # Create some other 
        self.other = OAUser.objects.create(
            realname="Other", email="Other@gmail.com", password="111111",
            status=UserStatusChoices.ACTIVED, department=self.dept_other
        )

        # Create the normal staff
        self.staff = OAUser.objects.create(
            realname="Hanyu", email="Hanyu@gmail.com", password="111111", 
            status=UserStatusChoices.ACTIVED, department=self.dept_hr
        )

        # Fill the manager of each department
        self.dept_hr.manager = self.manager
        self.dept_hr.leader = self.manager
        self.dept_hr.save()

        # Create a leave type
        self.absent_type = AbsentType.objects.create(name="sick leave")

        # Create a request for leave
        self.absent = Absent.objects.create(
            title="Test Absent",
            request_content="I need a rest",
            absent_type=self.absent_type,
            requester=self.staff,
            responder=self.manager,
            status=AbsentStatusChoices.AUDITING,
            start_date="2026-03-01",
            end_date="2026-03-02",
        )
    
    def test_only_responder_can_approve(self):
        # Fake a request
        class FakeRequest:
            def __init__(self, user):
                self.user = user

        # Other people try to approve the request, should failed
        req = FakeRequest(self.other)
        ser = AbsentSerializer(
            instance=self.absent,
            data={"status": AbsentStatusChoices.PASS},
            context={"request": req},
            partial=True
        )
        ser.is_valid()
        with self.assertRaises(exceptions.AuthenticationFailed):
            ser.save()

        # 2. the staff try to approve, also should failed
        req = FakeRequest(self.staff)
        ser = AbsentSerializer(
            instance=self.absent,
            data={"status": AbsentStatusChoices.PASS},
            context={"request": req},
            partial=True
        )
        ser.is_valid()
        with self.assertRaises(exceptions.AuthenticationFailed):
            ser.save()

        # 3. The manager try ro approve, finally succeed!
        req = FakeRequest(self.manager)
        ser = AbsentSerializer(
            instance=self.absent,
            data={
                "status": AbsentStatusChoices.PASS,
                "response_content": "Approved"
            },
            context={"request": req},
            partial=True
        )
        self.assertTrue(ser.is_valid())
        ser.save()

        # make sure the status was changed
        self.absent.refresh_from_db()
        self.assertEqual(self.absent.status, AbsentStatusChoices.PASS)

        
    def test_cannot_update_already_confirmed_absent(self):
        # change the status
        self.absent.status = AbsentStatusChoices.PASS
        self.absent.save()

        class FakeRequest:
            def __init__(self, user):
                self.user = user

        # The manager try to aprrove again, should fail!
        req = FakeRequest(self.manager)
        ser = AbsentSerializer(
            instance=self.absent,
            data={"status": AbsentStatusChoices.REJECT},
            context={"request": req},
            partial=True
        )
        ser.is_valid()
        with self.assertRaises(exceptions.APIException):
            ser.save()