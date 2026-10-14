from django import forms
from django.db.models import Case as SQLCase, When
from django.utils.html import format_html

from account.models import Language

from .models import Case


LANGUAGE_NAMES = ["Hungarian", "English", "German"]

FORMAT_CHOICES = [
    ("either", "Either"),
    ("in_person", "In-person"),
    ("online", "Online"),
]


class SuffixNumberInput(forms.NumberInput):
    """Number input that renders a text suffix (e.g. 'Ft') right after the field."""

    def __init__(self, suffix="", attrs=None):
        super().__init__(attrs)
        self.suffix = suffix

    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        return format_html('{} <span class="input-suffix">{}</span>', html, self.suffix)


class CaseForm(forms.ModelForm):
    description = forms.CharField(
        label="Description",
        required=True,
        min_length=30,
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Placeholder example case description",
                "rows": 6,
            }
        ),
    )

    city = forms.CharField(
        label="City",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "e.g. Budapest"}),
    )

    language = forms.ModelMultipleChoiceField(
        label="Language",
        required=False,
        queryset=Language.objects.none(),  # set in __init__
        widget=forms.CheckboxSelectMultiple,
    )

    format = forms.ChoiceField(
        label="Format",
        choices=FORMAT_CHOICES,
        initial="either",
        widget=forms.RadioSelect,
    )

    hourly_rate = forms.DecimalField(
        label="Max hourly rate",
        required=False,
        min_value=0,
        max_digits=8,
        decimal_places=2,
        widget=SuffixNumberInput(suffix="Ft", attrs={"placeholder": "60000"}),
    )

    class Meta:
        model = Case
        fields = ["description", "city", "language", "format", "hourly_rate"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only the three languages, always in the order Hungarian, English, German.
        order = SQLCase(
            *[When(name=name, then=pos) for pos, name in enumerate(LANGUAGE_NAMES)]
        )
        language_field = self.fields["language"]
        language_field.queryset = Language.objects.filter(
            name__in=LANGUAGE_NAMES
        ).order_by(order)
        language_field.label_from_instance = lambda obj: obj.name
