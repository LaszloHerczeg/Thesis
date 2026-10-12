from django.db import models


MODE_CHOICES = [("rule-based", "Rule_based"), ("llm_based", "LLM-based")]

class Rule(models.Model):
    category = models.ForeignKey('case.Category', on_delete=models.CASCADE)
    expression = models.TextField()
    is_positive =models.BooleanField(default=True)
    is_active =models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rule: {self.category.name} - {self.expression}"


class Classification(models.Model):
    case = models.ForeignKey('case.Case', on_delete=models.CASCADE)
    predicted_category = models.ForeignKey('case.Category', on_delete=models.CASCADE)
    mode = models.CharField(choices=MODE_CHOICES, default=MODE_CHOICES[0])
    rules_applied = models.ManyToManyField(Rule)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Case: {self.case} - Predicted category {self.predicted_category.name} - Created at: {self.created_at}"
