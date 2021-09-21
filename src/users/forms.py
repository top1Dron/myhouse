from django import forms


class LoginForm(forms.Form):
    email = forms.CharField(max_length=200, required=True, widget=forms.EmailInput())
    password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput())