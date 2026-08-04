# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, StudentProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin for the custom, email-based user model. Reuses Django's built-in
    UserAdmin layout but swaps username -> email and adds our custom fields.
    """
    model = CustomUser
    ordering = ["email"]
    list_display = ["email", "full_name", "role", "is_staff", "is_active"]
    list_filter = ["role", "is_staff", "is_active"]
    search_fields = ["email", "full_name"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name", "first_name", "last_name")}),
        ("Role & permissions", {
            "fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            # Fields shown on the "Add user" form in /admin/
            "fields": ("email", "full_name", "role", "password1", "password2"),
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "student_number", "program", "year_of_study"]
    search_fields = ["user__email", "user__full_name", "student_number"]
