# backend/apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from .models import User


class UserCreationForm(forms.ModelForm):
    """A form for creating new users."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('discord_id', 'username', 'email')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users."""
    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text=(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            '<a href="../password/">this form</a>.'
        ),
    )

    class Meta:
        model = User
        fields = ('discord_id', 'username', 'email', 'password', 'is_active', 'is_admin', 'is_staff')

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('discord_id', 'username', 'email', 'is_admin', 'is_staff', 'is_active')
    list_filter = ('is_admin', 'is_staff', 'is_active', 'recruit_status', 'officer_candidate', 'warrant_officer_candidate')
    fieldsets = (
        (None, {'fields': ('discord_id', 'username', 'email', 'password')}),
        ('Personal info', {'fields': ('avatar_url', 'bio', 'service_number')}),
        ('Military info', {'fields': ('current_rank', 'primary_unit', 'branch', 'commission_stage')}),
        ('Status', {'fields': ('onboarding_status', 'recruit_status', 'officer_candidate', 'warrant_officer_candidate')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'join_date')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('discord_id', 'username', 'email', 'password1', 'password2'),
        }),
    )
    search_fields = ('discord_id', 'username', 'email')
    ordering = ('discord_id',)
    filter_horizontal = ('groups', 'user_permissions',)


# Register the custom admin
admin.site.register(User, UserAdmin)