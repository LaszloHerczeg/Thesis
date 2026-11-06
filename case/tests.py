from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from account.models import Language
from case.models import Case

User = get_user_model()

# Create your tests here.
class CreateCaseViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # runs once for the class
        cls.user = User.objects.create_user(username='testuser', password='password')
        cls.hungarian = Language.objects.create(name="Hungarian")
        cls.english = Language.objects.create(name="English")
        cls.german = Language.objects.create(name="German") # ez nem lesz kiválasztva

    def setUp(self):
        # runs before each test
        # skips the authentication (authentication should be separate tests)
        self.client.force_login(self.user)
        self.url = reverse("case:create_case")
        self.valid_data = {
            "title": "Test Case",
            "description": "Test Case Description",
            "language": [self.hungarian.pk, self.english.pk],
        }

        def _fake_classification(self):
            return MagicMock(pk=1)

        def _assert_case_saved_correctly(self, case):
            self.assertEqual(case.user, self.user)
            self.assertEqual(case.title, self.valid_data["title"])
            self.assertEqual(case.description, self.valid_data["description"])
            self.assertEqual(case.status, Case.Status.IN_PROGRESS)
            self.assertIsNone(case.category)
            # M2M does not have a guaranteed order, so I use set
            self.assertEqual(
                set(case.language.values_list("pk", flat=True)),
                {self.hungarian.pk, self.english.pk},
            )

