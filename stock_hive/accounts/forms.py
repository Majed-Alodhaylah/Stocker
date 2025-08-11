from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

ROLE_CHOICES = (("employee", "Employee"), ("admin", "Admin"))

class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES, initial="employee",
                             widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ["username", "password1", "password2", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.help_text = ""
            cls = f.widget.attrs.get("class", "")
            f.widget.attrs["class"] = (cls + " form-control").strip()
        self.fields["role"].widget.attrs.pop("class", None)
