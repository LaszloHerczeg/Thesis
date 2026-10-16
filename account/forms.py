from django import forms
from django.contrib.auth.password_validation import password_validators_help_text_html, validate_password
from django.core.exceptions import ValidationError

from account.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True

class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    first_name = forms.CharField(label='First Name', max_length=100, required=False)
    last_name = forms.CharField(label='Last Name', max_length=100, required=False)
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password', help_text=password_validators_help_text_html)
    password_confirmation = forms.CharField(widget=forms.PasswordInput, label='Confirm Password', help_text="Enter the same password as before, for verification.")

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password and password_confirmation and password != password_confirmation:
            self.add_error("password_confirmation", "Passwords do not match.")

        if password:
            user = User(
                username = cleaned_data.get("username", ""),
                email = cleaned_data.get("email", ""),
                first_name = cleaned_data.get("first_name", ""),
                last_name = cleaned_data.get("last_name", ""),
            )
            try:
                validate_password(password, user = user)
            except ValidationError as e:
                self.add_error("password", e)

        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

    def clean_username(self):
        username = self.cleaned_data["username"]
        return username

    def clean_password(self):
        password = self.cleaned_data["password"]
        return password