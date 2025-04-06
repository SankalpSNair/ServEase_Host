from django import forms

class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')