from django.contrib import admin

from evaluation.models import EvalRun, EvalCase, EvalClassification

# Register your models here.
@admin.register(EvalRun)
class EvalRunAdmin(admin.ModelAdmin):
    list_display = ("id", "mode", "created_at", "duration", "accuracy_display")
    readonly_fields = ("created_at", "duration")

    @admin.display(description="Accuracy", ordering="accuracy")
    def accuracy_display(self, obj):
        """
        Displays the accuracy of the run as a percentage rounded to three decimal places
        """
        if obj.accuracy is None:
            return "-"
        return f"{obj.accuracy:.3%}%"



admin.site.register(EvalCase)
admin.site.register(EvalClassification)