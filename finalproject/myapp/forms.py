from django import forms
from .models import Image
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
# models User
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        ]

        labels = {
            'username': 'Username',
            'first_name': 'First Name',
            'last_name': 'Last Name',   
            'email': 'Email',
            'password': 'Password',
        }
        

class VisibleMultipleHiddenInput(forms.widgets.HiddenInput):
    def render(self, name, value, attrs=None, renderer=None):
        if not attrs:
            attrs = {}
        attrs["type"] = "hidden"  # Change the input type to 'hidden'
        return mark_safe(super().render(name, value, attrs, renderer))


class ImageForm(forms.ModelForm):
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise ValidationError(self.error_messages['image'])
        return image

    class Meta:
        model = Image
        fields = [
            'uploader',
            'image',
            'distance',
            'color',
        ]
        labels = {
            'uploader': 'Uploader',
            'image': 'Image',
            'distance': 'Distance',
            'color': 'Color',
        }
        widgets = {
            'image': forms.FileInput(
                attrs={'class': 'form-control', 'placeholder': 'Image', 'accept': 'image/*'}
            ),
            'distance': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Distance', 'min': 0, 'max': 100, 'step': 1}
            ),
            'color': forms.Select(
                attrs={
                    'class': 'form-control', 
                    'placeholder': 'Color',
                    'data-live-search': 'true',
                    'data-size': '5',
                    
                }
            ),
        }
        allow_empty_file = False
        error_messages = {
            'uploader': {
                'required': "Uploader is required but hidden",
            },
            'image': {
                'required': "Image is required but hidden",
            },
        }