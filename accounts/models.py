from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier for authentication
    instead of usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email address must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom User model supporting Student and Admin roles with email authentication.
    """
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        ADMIN = 'ADMIN', 'Admin'

    username = None  # Remove standard username field
    email = models.EmailField('University Email', unique=True, db_index=True)
    full_name = models.CharField('Full Name', max_length=255)
    role = models.CharField(
        max_length=10, 
        choices=Role.choices, 
        default=Role.STUDENT
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class StudentProfile(models.Model):
    """
    Stores academic and program information for student accounts.
    """
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    student_number = models.CharField(
        'Student Number', 
        max_length=20, 
        unique=True, 
        db_index=True
    )
    program = models.CharField('Program / Course of Study', max_length=150)
    year_of_study = models.PositiveSmallIntegerField(
        'Year of Study',
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        default=1
    )

    class Meta:
        db_table = 'student_profile'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'

    def __str__(self):
        return f"{self.user.full_name} - {self.student_number} ({self.program})"