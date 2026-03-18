from django.test import TestCase
from rest_framework import exceptions
from oaauth.models import OAUser, OADepartment, UserStatusChoices


class OAUserCoreTest(TestCase):

    def setUp(self):
        #1. Create the department
        self.dept_board = OADepartment.objects.create(
            name="Board Department",
            leader=None,
            manager=None
        )
        self.dept_hr = OADepartment.objects.create(
            name="HR Department",
            leader=None,
            manager=None
        )

        # 2. Create the staffs
        # Leader of board department
        self.board_user = OAUser.objects.create_superuser(
            realname="Board Leader",
            email="board@test.com",
            password="123456",
            department=self.dept_board
        )
        # leader of HR department
        self.hr_leader = OAUser.objects.create_superuser(
            realname="HR Leader",
            email="hr.leader@test.com",
            password="123456",
            department=self.dept_hr
        )
        # manager of HR department
        self.hr_manager = OAUser.objects.create_superuser(
            realname="HR Manager",
            email="hr.manager@test.com",
            password="123456",
            department=self.dept_hr
        )
        # normal staff
        self.hr_staff = OAUser.objects.create_user(
            realname="HR Staff",
            email="hr.staff@test.com",
            password="123456",
            department=self.dept_hr
        )

        # 3. set the leader and manager to the department
        self.dept_board.leader = self.board_user
        self.dept_board.manager = None
        self.dept_board.save()

        self.dept_hr.leader = self.hr_leader
        self.dept_hr.manager = self.hr_manager
        self.dept_hr.save()

    # ======================
    # Test1: Create users
    # ======================
    def test_user_creation_basic(self):
        self.assertEqual(self.hr_staff.realname, "HR Staff")
        self.assertEqual(self.hr_staff.email, "hr.staff@test.com")
        self.assertTrue(self.hr_staff.check_password("123456"))
        self.assertEqual(self.hr_staff.status, UserStatusChoices.UNACTIVE)
        self.assertEqual(self.hr_staff.department.name, "HR Department")
        self.assertFalse(self.hr_staff.is_superuser)

    # ======================
    # Test2: Create super user
    # ======================
    def test_create_superuser(self):
        self.assertTrue(self.hr_manager.is_superuser)
        self.assertTrue(self.hr_manager.is_staff)
        self.assertEqual(self.hr_manager.status, UserStatusChoices.ACTIVED)

    # ======================
    # Test3: Make sure the staffs are belong to the department
    # ======================
    def test_user_department_relation(self):
        #hr staff belongs to HR department
        self.assertEqual(self.hr_staff.department, self.dept_hr)
        # The number of members of HR department
        self.assertEqual(self.dept_hr.staffs.count(), 3)
        # leader_department
        self.assertEqual(self.hr_leader.department, self.dept_hr)
        # manager_department
        self.assertEqual(self.hr_manager.department, self.dept_hr)

    # ======================
    # Test4: Test the enum type
    # ======================
    def test_user_status_choices(self):
        unactive_user = OAUser.objects.create_user(
            realname="Unactive",
            email="unactive@test.com",
            password="123456",
            status=UserStatusChoices.ACTIVED
        )
        self.assertEqual(unactive_user.status, UserStatusChoices.ACTIVED)

        locked_user = OAUser.objects.create_user(
            realname="Locked",
            email="locked@test.com",
            password="123456",
            status=UserStatusChoices.LOCKED
        )
        self.assertEqual(locked_user.status, UserStatusChoices.LOCKED)

    # ======================
    # Test5: The core fields of department
    # ======================
    def test_department_fields(self):
        self.assertEqual(self.dept_hr.name, "HR Department")
        self.assertEqual(self.dept_hr.leader, self.hr_leader)
        self.assertEqual(self.dept_hr.manager, self.hr_manager)
        self.assertIsNone(self.dept_board.manager)
        self.assertEqual(self.dept_board.leader, self.board_user)