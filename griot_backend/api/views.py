from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, AuthenticationSerializer, ProfileSerializer, AccountSerializer
from profiles.models import Profile
from accounts.models import Account
from django.shortcuts import get_object_or_404

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes =[permissions.AllowAny]

class AuthenticateUserView(generics.CreateAPIView):
    serializer_class = AuthenticationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=200)

class LogoutView(generics.GenericAPIView):
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({"detail": "User logged out successfully."})

class UpdateProfileView(generics.UpdateAPIView):
    http_method_names = ['patch']
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    
    def get_object(self):
        user_id = self.kwargs['pk']
        profile = Profile.objects.get(user__id=user_id)
        return profile

class CreateAccountView(generics.CreateAPIView):
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountSerializer
    queryset = Account.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner_user=self.request.user)
    

class UpdateAccountView(generics.UpdateAPIView):
    http_method_names = ['patch']
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountSerializer
    queryset = Account.objects.all()

class AddBelovedOneToAccountView(generics.CreateAPIView):
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated]
    queryset = Account.objects.all()

    def create(self, request, *args, **kwargs):
        account = self.get_object()
        beloved_one_id = kwargs.get('beloved_one_id')
        beloved_one = get_object_or_404(User, pk=beloved_one_id)
        account.beloved_ones.add(beloved_one)
        return Response({'message': 'Beloved one added successfully.'})
    
class RemoveBelovedOneFromAccountView(generics.CreateAPIView):
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated]
    queryset = Account.objects.all()

    def create(self, request, *args, **kwargs):
        account = self.get_object()
        beloved_one_id = kwargs.get('beloved_one_id')
        beloved_one = get_object_or_404(User, pk=beloved_one_id)
        account.beloved_ones.remove(beloved_one)
        return Response({'message': 'Beloved one removed successfully.'})

