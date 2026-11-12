from django.db import models

from case.models import Category, BaseCase
from classification.models import Rule, BaseClassification, ClassificationMode


class EvalCase(BaseCase):
    key = models.CharField(max_length=100)
    expected_category = models.ForeignKey(Category, related_name="%(app_label)s_%(class)s_set", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_follow_up_expected = models.BooleanField(default=False)


class EvalRun(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(null=True)
    classifier_version = models.CharField(max_length=100)
    accuracy = models.FloatField(null=True)
    mode = models.CharField(choices=ClassificationMode.choices, default=ClassificationMode.RULE, max_length=100)

    @property
    def accuracy_percent(self):
        return self.accuracy * 100 if self.accuracy is not None else None


class EvalClassification(BaseClassification):
    case = models.ForeignKey(EvalCase, on_delete=models.CASCADE)
    run = models.ForeignKey(EvalRun, on_delete=models.CASCADE, related_name="results")
    passed = models.BooleanField(null=True, blank=True)
    is_follow_up_asked = models.BooleanField(default=False)
    duration = models.FloatField(null=True)
