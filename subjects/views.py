# subjects/views.py
from rest_framework import viewsets, permissions
from .models import Subject
from .serializers import SubjectSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Any authenticated user can read (GET, HEAD, OPTIONS).
    - Only Admins or Staff users can modify (POST, PUT, PATCH, DELETE).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        # Check role or staff status for write operations
        user_role = getattr(request.user, 'role', None)
        return user_role == 'ADMIN' or request.user.is_staff


class SubjectViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing the Subject catalog.
    Maps to the SUBJECT table.
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnly]