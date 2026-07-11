"""
accounts/admin.py

Registers Student with Django admin, extending the built-in UserAdmin
so we keep its password-hashing widget, permissions UI, etc., and just
add our one custom field (groupstudy_opt_in) on top.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Student


@admin.register(Student)
class StudentAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "groupstudy_opt_in",
        "is_staff",
    )
    list_filter = UserAdmin.list_filter + ("groupstudy_opt_in",)

    # UserAdmin.fieldsets is a tuple of (title, {"fields": (...)}) pairs.
    # Add our field to the existing "Personal info" section rather than
    # inventing a whole new section for one boolean.
    fieldsets = UserAdmin.fieldsets + (
        ("GroupStudy", {"fields": ("groupstudy_opt_in",)}),
    )

    # Also expose it on the "add user" form, not just the edit form.
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("GroupStudy", {"fields": ("groupstudy_opt_in",)}),
    )
