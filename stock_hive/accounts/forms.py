from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = (("employee", "Employee"), ("admin", "Admin"))
    role = forms.ChoiceField(choices=ROLE_CHOICES, initial="employee", widget=forms.RadioSelect)
    admin_code = forms.CharField(required=False, label="Admin code", help_text="")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.help_text = ""
            cls = field.widget.attrs.get("class", "")
            if isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs["class"] = (cls + " form-check-input").strip()
            else:
                field.widget.attrs["class"] = (cls + " form-control").strip()

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")
        code = cleaned.get("admin_code", "")
        if role == "admin":
            if code != getattr(settings, "ADMIN_SIGNUP_CODE", ""):
                raise forms.ValidationError("Invalid admin code.")
        return cleaned
