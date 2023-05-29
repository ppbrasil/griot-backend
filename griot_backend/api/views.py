from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from .serializers import UserSerializer, AuthenticationSerializer, ProfileSerializer, AccountSerializer, CharacterSerializer

from django.contrib.auth.models import User
from profiles.models import Profile
from accounts.models import Account
from characters.models import Character

from rest_framework.permissions import IsAuthenticated, AllowAny
from griot_backend.permissions import IsObjectOwner, IsBelovedOne, IsRelatedAccountOwner, IsRelatedAccountBelovedOne


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes =[AllowAny]

class AuthenticateUserView(generics.CreateAPIView):
    serializer_class = AuthenticationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=200)

class LogoutView(generics.GenericAPIView):
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({"detail": "User logged out successfully."})

class UpdateProfileView(generics.UpdateAPIView):
    http_method_names = ['patch']
    permission_classes = [IsAuthenticated, IsObjectOwner]
    serializer_class = ProfileSerializer
        
    def get_object(self):
        user_id = self.kwargs['pk']
        profile = Profile.objects.get(user__id=user_id)
        return profile

class CreateAccountView(generics.CreateAPIView):
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer
    queryset = Account.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner_user=self.request.user)
    
class UpdateAccountView(generics.UpdateAPIView):
    http_method_names = ['patch']
    permission_classes = [IsAuthenticated, IsObjectOwner]
    serializer_class = AccountSerializer
    queryset = Account.objects.all().filter(is_active=True)

class DeleteAccountView(generics.UpdateAPIView):
    http_method_names = ['delete']
    permission_classes = [IsAuthenticated, IsObjectOwner]
    serializer_class = AccountSerializer
    queryset = Account.objects.all().filter(is_active=True)

    def delete(self, request, pk):
        account = self.get_object()
        account.is_active = False
        account.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AddBelovedOneToAccountView(generics.CreateAPIView):
    http_method_names = ['post']
    permission_classes = [IsAuthenticated, IsObjectOwner]
    queryset = Account.objects.all()

    def create(self, request, *args, **kwargs):
        account = self.get_object()
        beloved_one_id = kwargs.get('beloved_one_id')
        beloved_one = get_object_or_404(User, pk=beloved_one_id)
        account.beloved_ones.add(beloved_one)
        return Response({'message': 'Beloved one added successfully.'})
    
class RemoveBelovedOneFromAccountView(generics.CreateAPIView):
    http_method_names = ['post']
    permission_classes = [IsAuthenticated, IsObjectOwner]
    queryset = Account.objects.all()

    def create(self, request, *args, **kwargs):
        account = self.get_object()
        beloved_one_id = kwargs.get('beloved_one_id')
        beloved_one = get_object_or_404(User, pk=beloved_one_id)
        account.beloved_ones.remove(beloved_one)
        return Response({'message': 'Beloved one removed successfully.'})

class CreateCharacterView(generics.CreateAPIView):
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated, IsRelatedAccountOwner]

class UpdateCharacterView(generics.UpdateAPIView):
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated, IsRelatedAccountOwner]
    queryset = Character.objects.all().filter(is_active=True)   

class DeleteCharacterView(generics.UpdateAPIView):
    http_method_names = ['delete']
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated, IsRelatedAccountOwner]
    queryset = Character.objects.all().filter(is_active=True)

    def delete(self, request, pk):
        character = self.get_object()
        character.is_active = False
        character.save()
        return Response(status=status.HTTP_204_NO_CONTENT)