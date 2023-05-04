from django import forms
from django.core import validators
from django.contrib.auth.models import User

class JoinForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput(attrs={'autocomplete':'new-password'}))
    email = forms.CharField(widget = forms.TextInput(attrs={'size': '30'}))
    class Meta():
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        help_texts = {
            'username': None
        }

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

SHOE_CHOICES= [
    ('Running', 'Running'),
    ('Basketball', 'Basketball'),
    ('Approach', 'Approach'),
    ('Climbing', 'Climbing'),
    ('Crossfit', 'Crossfit'),
    ('Cycling', 'Cycling'),
    ('Football', 'Football'),
    ]

#CUSHIONING_CHOICES= [
#    ('All', 'All'),
#    ('Plush', 'Plush'),
#    ('Firm', 'Firm'),
#    ('Balanced', 'Balanced'),
#    ]

class FilterForm(forms.Form):
    Shoe = forms.CharField(widget=forms.Select(choices=SHOE_CHOICES))
#    Cushioning = forms.CharField(widget=forms.Select(choices=CUSHIONING_CHOICES))
