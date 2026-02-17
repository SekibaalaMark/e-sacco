from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="Admin").exists()
    


class IsTreasurer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="Treasurer").exists()
    

class IsOrdinary(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="Ordinary").exists()
    


class CanPromoteUsers(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Superuser can promote
        if user.is_superuser:
            return True
        
        # Admin group can promote
        return user.groups.filter(name="Admin").exists()
