from django.contrib import admin
from .models import SalonAccount, CustomUser
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.utils.translation import gettext, gettext_lazy as _

# class CustomUserAdmin(UserAdmin):
#     # list_display = ('email',)
#     # ordering = ('email',)
#     pass

# # Register your models here.
# admin.site.register(SalonAccount)
# admin.site.register(CustomUser)


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email',)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances
    add_form = UserCreationForm
    list_display = ("email", "date_joined", 'salonAcc')
    ordering = ("email",)

    # fieldsets = (
    #     (None, {'fields': ('email', 'password', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active', 'avatar', 'salonAccount')}),
    #     )
    fieldsets = (
        (None, {'fields': ( 'email','password', 'salonAcc')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active', 'avatar', 'salonAcc')}
            ),
        )

    filter_horizontal = ()

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SalonAccount)
