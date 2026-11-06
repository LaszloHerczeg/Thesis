import uuid

from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class BaseCase(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'In Progress'
        DONE = 'done', 'Done'
        MORE_INFORMATION_NEEDED = 'more_information_needed', 'More information needed'
        NOT_SUPPORTED = 'not_supported', 'Not supported'
        FAILED = 'failed', 'Failed'

    description = models.TextField(max_length=500)
    status = models.CharField(choices=Status.choices, max_length=50, default='in_progress')
    error = models.TextField(blank=True, null=True)
    predicted_category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Case(BaseCase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    language = models.ManyToManyField('account.Language', blank=True)
    format = models.CharField(max_length=100)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)


    def __str__(self):
        return f"{self.user.username}'s case created at {self.created_at}"

    def list_language(self):
        return ", ".join(str(language) for language in self.language.all())

    class Meta:
        permissions = [
            ("view_all_cases", "Can view all cases"),
        ]

    def get_absolute_url(self):
        return reverse('case:case_detail', args=[self.pk])