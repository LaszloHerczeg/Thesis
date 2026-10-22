from django import forms

from account.models import Language
from case.models import Case

FORMAT_CHOICES = [
    ('either', 'Either'),
    ('in_person', 'In person'),
    ('online', 'Online')
]

NONE = "none"


class SearchForm(forms.Form):
    query = forms.CharField(label='Search:',
                            required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'Search...'},
                            ))
    field = forms.ChoiceField(label="Search in:",
                              required=True,
                              widget=forms.Select(),
                              choices=[('description', 'Description'), ('category', 'Category')],
                              )

class CaseForm(forms.ModelForm):
    description = forms.CharField(
        label='Description:',
        required=True,
        min_length=30,
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Placeholder example case description...',
                'rows':6
            }
        )
    )

    city = forms.CharField(
        label='City:',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Budapest'}),
    )

    language = forms.ModelMultipleChoiceField(
        label='Language:',
        required=False,
        queryset=Language.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )

    format = forms.ChoiceField(
        label='Format:',
        choices=FORMAT_CHOICES,
        initial='either',
        widget=forms.RadioSelect(),
    )

    hourly_rate = forms.DecimalField(
        label='Max hourly rate (Ft):',
        required=False,
        min_value=0,
        max_digits=8,
        decimal_places=2,
        step_size=1000,
        widget=forms.NumberInput(attrs={'placeholder': '60000'}),
    )

    class Meta:
        model = Case
        fields = ['description', 'city', 'language', 'format', 'hourly_rate']



class ClarifyForm(forms.Form):
    def __init__(self, *args, keywords, **kwargs):
        super().__init__(*args, **kwargs)
        for i, (keyword, phrases) in enumerate(keywords.items()):
            choices = [(p, p.capitalize()) for p in phrases] + [(NONE, "Egyik sem")]
            self.fields[f"q{i}"] = forms.ChoiceField(
                label=f"Mire gondolt a „{keyword}” kifejezésnél?",
                choices=choices,
                widget=forms.RadioSelect,
            )

    def chosen_phrases(self):
        return [v for v in self.cleaned_data.values() if v != NONE]