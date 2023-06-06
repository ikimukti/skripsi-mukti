from django import forms
from .models import Image
from django.utils.safestring import mark_safe

class VisibleMultipleHiddenInput(forms.widgets.HiddenInput):
    def render(self, name, value, attrs=None, renderer=None):
        if not attrs:
            attrs = {}
        attrs['type'] = 'hidden'  # Change the input type to 'hidden'
        return mark_safe(super().render(name, value, attrs, renderer))

class ImageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = True
    
    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        if not image:
            raise forms.ValidationError("Image is required 2")
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
            'image': VisibleMultipleHiddenInput(
                attrs={
                    'multiple': True,
                    'accept': 'image/*',
                    'type': 'file',
                    'required': True,
                    }
                ),
            'distance': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
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