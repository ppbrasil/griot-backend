from rest_framework import permissions
from accounts.models import Account

class IsObjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            return obj.user == request.user
        except: 
            return obj.owner_user == request.user

class IsBelovedOne(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.beloved_ones.all()

class IsRelatedAccountOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        account_id = request.data.get('account')
        if account_id is not None:
            try:
                account = Account.objects.get(id=account_id)
                return account.owner_user == request.user
            except Account.DoesNotExist:
                return False
        return True

    def has_object_permission(self, request, view, obj):
        # If the object has an `account` attribute
        if hasattr(obj, 'account'):
            return obj.account.owner_user == request.user
        return False
        
class IsRelatedAccountBelovedOne(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            account_id = request.data.get('account_id')
            account = Account.objects.get(id=account_id)
            return request.user in account.beloved_ones.all()
        except Account.DoesNotExist:
            return False
        
        
  