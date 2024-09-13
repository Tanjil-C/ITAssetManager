"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from .models import Equipment, Employee

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class EquipmentForm(forms.ModelForm):
    purchased_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        )
    )

    class Meta:
        model = Equipment
        fields = ['name', 'description', 'purchased_date', 'serial_number', 'condition_status', 'usage_status', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'condition_status': forms.Select(attrs={'class': 'form-control'}),
            'usage_status': forms.Select(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AssignEquipmentForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        empty_label="No user"
    )
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        equipment = cleaned_data.get('equipment')

        if equipment:
            if employee:
                # Check if the equipment is already assigned to the employee
                if equipment in employee.equipment.all():
                    self.add_error('equipment', 'This equipment is already assigned to the selected employee.')

            # Check if there is stock available
            if equipment.stock <= 0:
                self.add_error('equipment', 'There is no stock available for this equipment.')

        return cleaned_data

class EmployeeForm(forms.ModelForm):
    hire_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        )
    )

    phone_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d+$', 'Enter a valid phone number.')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'tel',
            'pattern': r'^\d+$',
            'title': 'Enter a valid phone number.'
        })
    )

    equipment = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'position', 'hire_date', 'equipment']
        widgets = {
            'position': forms.Select(attrs={'class': 'form-control'}),
        }
