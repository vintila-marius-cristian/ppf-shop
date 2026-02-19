from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    consent = forms.BooleanField(
        required=True,
        label="Sunt de acord cu politica de confidentialitate",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    company = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nume complet"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@exemplu.ro"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+40"}),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Subiect solicitare"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Spune-ne ce masina ai si ce serviciu doresti"}),
        }

    def clean_company(self) -> str:
        value = self.cleaned_data.get("company", "")
        if value:
            raise forms.ValidationError("Spam detected.")
        return value

    def clean_message(self) -> str:
        value = self.cleaned_data.get("message", "").strip()
        if len(value) < 15:
            raise forms.ValidationError("Mesajul trebuie sa contina minim 15 caractere.")
        return value


class OwnerLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
        label="Utilizator",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Parola"}),
        label="Parola",
    )
