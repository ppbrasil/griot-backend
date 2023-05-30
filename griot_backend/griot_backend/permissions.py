from django.contrib.auth.models import User
from rest_framework import permissions
from accounts.models import Account
from memories.models import Memory, Video
from profiles.models import Profile
from characters.models import Character


class ProfilePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Owners can perform any operation
        if request.user == obj.user:
            return True
        # Beloved ones can read profiles
        elif request.method in permissions.SAFE_METHODS:
            return request.user in obj.user.account_set.filter(beloved_ones=request.user)
        # Deny if none of the above
        return False

class AccountPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Owners can perform any operation
        if request.user == obj.owner_user:
            return True
        # Beloved ones can only read account details
        elif request.method in permissions.SAFE_METHODS and request.user in obj.beloved_ones.all():
            return True
        # Deny if none of the above
        return False

class MemoryPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Owners can perform any operation
        if request.user == obj.account.owner_user:
            return True
        # Beloved ones can only read memory details
        elif request.method in permissions.SAFE_METHODS and request.user in obj.account.beloved_ones.all():
            return True
        # Deny if none of the above
        return False

class CharacterPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Owners can perform any operation
        if request.user == obj.account.owner_user:
            return True
        # Beloved ones can only read memory details
        elif request.method in permissions.SAFE_METHODS and request.user in obj.account.beloved_ones.all():
            return True
        # Deny if none of the above
        return False

class VideoPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Owners can perform any operation
        if request.user == obj.memory.account.owner_user:
            return True
        # Beloved ones can only read video details
        elif request.method in permissions.SAFE_METHODS and request.user in obj.memory.account.beloved_ones.all():
            return True
        # Deny if none of the above
        return False