from django import forms
from .models import Image
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError

class VisibleMultipleHiddenInput(forms.widgets.HiddenInput):
    def render(self, name, value, attrs=None, renderer=None):
        if not attrs:
            attrs = {}
        attrs["type"] = "hidden"  # Change the input type to 'hidden'
        return mark_safe(super().render(name, value, attrs, renderer))

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
            'image': VisibleMultipleHiddenInput(
                attrs={
                    "multiple": True,
                    "class": "block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100 cursor-pointer",
                    "id": "image-field",
                    "accept": "image/*",
                    "type": "file",
                },
            ),
            'distance': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Distance', 'min': 0, 'max': 100, 'step': 1}
            ),
            'color': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Color', 'maxlength': 20}
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