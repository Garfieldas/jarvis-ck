from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from app.models import User


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "placeholder": "Enter your email",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].label = "Password"
        self.fields["password"].widget.attrs.update(
            {
                "autocomplete": "current-password",
                "placeholder": "Enter your password",
            }
        )


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "placeholder": "Enter your email",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Password"
        self.fields["password1"].widget.attrs.update(
            {
                "autocomplete": "new-password",
                "placeholder": "Create a password",
            }
        )
        self.fields["password2"].label = "Confirm password"
        self.fields["password2"].widget.attrs.update(
            {
                "autocomplete": "new-password",
                "placeholder": "Repeat your password",
            }
        )


class TrainModelForm(forms.Form):
    num_epochs = forms.IntegerField(
        label="Epochs",
        min_value=1,
        max_value=500,
        initial=30,
        help_text="Lower values train faster; higher values may improve quality.",
        widget=forms.NumberInput(
            attrs={
                "placeholder": "30",
                "class": "mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm",
            }
        ),
    )


class PredictSmilesForm(forms.Form):
    smiles = forms.CharField(
        label="SMILES",
        max_length=1000,
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. CC(=O)Oc1ccccc1C(=O)O",
                "class": "mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm",
            }
        ),
    )
    threshold = forms.FloatField(
        label="Activity threshold",
        min_value=0.0,
        max_value=1.0,
        initial=0.5,
        widget=forms.NumberInput(
            attrs={
                "step": "0.01",
                "class": "mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm",
            }
        ),
    )
