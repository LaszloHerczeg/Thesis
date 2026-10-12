from django.db import models


class Recommendation(models.Model):
    case = models.ForeignKey('case.Case', on_delete=models.CASCADE, related_name='recommendation')
    lawyer = models.ForeignKey('account.Lawyer', on_delete=models.CASCADE, related_name='recommendation')
    rank = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "rank"]

    def __str__(self):
        return f"Recommendation for Case: {self.case} - Lawyer: {self.lawyer} - rank: {self.rank}"