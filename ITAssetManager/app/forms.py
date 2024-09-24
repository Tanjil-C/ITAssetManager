"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.models import User
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

from django.core.exceptions import ValidationError

# Custom user registration form with password confirmation validation
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

# Form to handle equipment data with customized widgets
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

# Form to assign equipment to employees with validation for equipment assignment
class AssignEquipmentForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        empty_label="No user"
    )
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )    
    
    # Clean method to check assignment and stock availability
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

# Employee form 
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

    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'position', 'hire_date']
        widgets = {
            'position': forms.Select(attrs={'class': 'form-control'}),
        }
