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

class ShoePreferenceForm(forms.Form):
    CHOICES = [
        ('Approach', 'Approach'),
        ('Basketball', 'Basketball'),
        ('Climbing', 'Climbing'),
        ('Cross Fit', 'Cross Fit'),
        ('Football', 'Football'),
        ('Golf', 'Golf'),
        ('Hiking', 'Hiking'),
        ('Running', 'Running'),
        ('Sneaker', 'Sneaker'),
        ('Soccer', 'Soccer'),
        ('Tennis', 'Tennis'),
        ('Track', 'Track'),
        ('Trail', 'Trail'),
        ('Training', 'Training'),
        ('Walking', 'Walking'),
    ]
    preference = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple)
