from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    def __str__(self):
        return f'User: {self.username}'

class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name


class Lawyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialty = models.ManyToManyField('case.Category', related_name='lawyer_specialty')
    language = models.ManyToManyField(Language, blank=True, related_name='lawyer_language')
    city = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_online = models.BooleanField(default=False)
    def __str__(self):
        return f'Lawyer: {self.user.username}'

    def list_specialty(self):
        return ", ".join(str(category) for category in self.specialty.all())

    def list_language(self):
        return ", ".join(str(language) for language in self.language.all())

    def is_online(self):
        if self.is_online:
            return "online"
        else:
            return "in-person"







