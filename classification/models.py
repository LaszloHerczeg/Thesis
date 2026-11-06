from django.db import models

from case.models import Category

class ClassificationMode(models.TextChoices):
    RULE = "rule_based", "Rule-based classification"
    LLM = "llm", "LLM classification"

class Rule(models.Model):
    category = models.ForeignKey('case.Category', on_delete=models.CASCADE)
    expression = models.TextField()
    weight = models.FloatField()
    is_positive =models.BooleanField(default=True)
    is_active =models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["category", "expression"], name="unique_rule_category_expression"
            )
        ]

    def __str__(self):
        return f"Rule: {self.category.name} - {self.expression}"

class BaseClassification(models.Model):
    predicted_category = models.ForeignKey('case.Category', on_delete=models.CASCADE, blank=True, null=True)
    mode = models.CharField(choices=ClassificationMode.choices, default=ClassificationMode.RULE, max_length=50)
    is_matching_made = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Only Rule-based
    rules_applied = models.ManyToManyField(Rule)
    points = models.JSONField(default=dict, null=True, blank=True) # {"category_id": score}
    top_keywords = models.JSONField(default=list, null=True, blank=True)

    # Only LLM-based
    reasoning = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def get_chart_data(self):
        if self.mode == ClassificationMode.LLM:
            return {}
        ids = [int(cid) for cid in self.points]
        categories = Category.objects.in_bulk(ids)

        ranked = sorted(self.points.items(), key=lambda kv: kv[1], reverse=True)
        return  {
            "labels": [categories[int(cid)].name for cid, _ in ranked],
            "values": [score for _, score in ranked],
        }


class Classification(BaseClassification):
    case = models.ForeignKey('case.Case', on_delete=models.CASCADE)

    def __str__(self):
        return f"Case: {self.case} - Predicted category {self.predicted_category.name} - Created at: {self.created_at}"
