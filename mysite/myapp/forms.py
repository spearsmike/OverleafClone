from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from . import models

def must_be_unique(value):
    user = User.objects.filter(email=value)
    if len(user) > 0:
        raise forms.ValidationError("Email is already in use.")
    return value

class DocumentForm(forms.Form):
    document = forms.CharField(
        label="Document Name",
        required=True,
        max_length=50,
    )
    public = forms.BooleanField(
        label="Make Document Public",
        required=False   
    )

    def save(self, request):
        document_instance = models.DocumentModel()
        document_instance.docName = self.cleaned_data["document"]
        document_instance.public = self.cleaned_data["public"]
        document_instance.contents = ""
        document_instance.author = request.user
        user_instance = User.objects.filter(id=request.user.id)
        document_instance.save()
        document_instance.editors.set(user_instance)
        return document_instance

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        validators=[must_be_unique]
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
