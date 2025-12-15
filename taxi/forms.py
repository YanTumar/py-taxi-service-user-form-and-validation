from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CheckboxSelectMultiple

from taxi.models import Car


class CarForm(ModelForm):
    drivers = ModelForm.Meta.model.drivers.field.rel.to.objects.all()

    class Meta:
        model = Car
        fields = "__all__"
        widgets = {"drivers": CheckboxSelectMultiple(), }


class DriverCreationForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "license_number",
            "password",
        )

    def clean_license_number(self):
        license_number = self.cleaned_data["license_number"]

        return license_number

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise ValidationError("Passwords don't match")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class DriverLicenseUpdateForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("license_number",)

    def clean_license_number(self):
        license_number = self.cleaned_data["license_number"]

        return license_number
