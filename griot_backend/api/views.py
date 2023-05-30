from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from .serializers import UserSerializer, AuthenticationSerializer, ProfileSerializer, AccountSerializer, CharacterSerializer, UserAccountSerializer, MemorySerializer, VideoSerializer

from django.contrib.auth.models import User
from profiles.models import Profile
from accounts.models import Account
from characters.models import Character
from memories.models import Memory, Video

from rest_framework.permissions import IsAuthenticated, AllowAny
from griot_backend.permissions import (
    ProfilePermissions, 
    AccountPermissions, 
    CharacterPermissions, 
    MemoryPermissions, 
    VideoPermissions,
)

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
    permission_classes = [IsAuthenticated, ProfilePermissions]
    serializer_class = ProfileSerializer
        
    def get_object(self):
        user_id = self.kwargs['pk']
        profile = Profile.objects.get(user__id=user_id)
        return profile

class CreateAccountView(generics.CreateAPIView):
    http_method_names = ['post']
    permission_classes = [IsAuthenticated, AccountPermissions]
    serializer_class = AccountSerializer
    queryset = Account.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner_user=self.request.user)
    
class ListUserAccountsViews(generics.RetrieveAPIView):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]
    serializer_class = UserAccountSerializer
    
    def get_object(self):
        return self.request.user

class UpdateAccountView(generics.UpdateAPIView):
    http_method_names = ['patch']
    permission_classes = [IsAuthenticated, AccountPermissions]
    serializer_class = AccountSerializer
    queryset = Account.objects.all().filter(is_active=True)

class DeleteAccountView(generics.UpdateAPIView):
    http_method_names = ['delete']
    permission_classes = [IsAuthenticated, AccountPermissions]
    serializer_class = AccountSerializer
    queryset = Account.objects.all().filter(is_active=True)

    def delete(self, request, pk):
        account = self.get_object()
        account.is_active = False
        account.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AddBelovedOneToAccountView(generics.UpdateAPIView):
    http_method_names = ['patch']
    permission_classes = [AccountPermissions]
    queryset = Account.objects.all()

    def update(self, request, *args, **kwargs):
        account = self.get_object()
        beloved_one_id = kwargs.get('beloved_one_id')
        beloved_one = get_object_or_404(User, pk=beloved_one_id)
        account.beloved_ones.add(beloved_one)
        return Response({'message': 'Beloved one added successfully.'})
    
class RemoveBelovedOneFromAccountView(generics.UpdateAPIView):
    http_method_names = ['patch']
    permission_classes = [AccountPermissions]
    queryset = Account.objects.all()

    def update(self, request, *args, **kwargs):
        account = self.get_object()
        beloved_one_id = kwargs.get('beloved_one_id')
        beloved_one = get_object_or_404(User, pk=beloved_one_id)
        account.beloved_ones.remove(beloved_one)
        return Response({'message': 'Beloved one removed successfully.'})

class ListBelovedOneFromAccountView(generics.RetrieveAPIView):
    http_method_names = ['get']
    queryset = Account.objects.all().filter(is_active=True)
    permission_classes = [IsAuthenticated, AccountPermissions]
    serializer_class = AccountSerializer
    lookup_field = 'pk'

class CreateCharacterView(generics.CreateAPIView):
    http_method_names = ['post']
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated, CharacterPermissions]

class UpdateCharacterView(generics.UpdateAPIView):
    http_method_names = ['patch']
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated, CharacterPermissions]
    queryset = Character.objects.all().filter(is_active=True)   

class DeleteCharacterView(generics.UpdateAPIView):
    http_method_names = ['delete']
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated, CharacterPermissions]
    queryset = Character.objects.all().filter(is_active=True)

    def delete(self, request, pk):
        character = self.get_object()
        character.is_active = False
        character.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CreateMemoryView(generics.CreateAPIView):
    http_method_names = ['post']
    serializer_class = MemorySerializer
    permission_classes = [IsAuthenticated, MemoryPermissions]

class RetrieveMemoryView(generics.RetrieveAPIView):
    queryset = Memory.objects.all()
    serializer_class = MemorySerializer
    permission_classes = [MemoryPermissions]


class CreateVideoMemoryView(generics.CreateAPIView):
    http_method_names =['post']
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated, MemoryPermissions]

    def perform_create(self, serializer):
        memory = Memory.objects.get(id=self.request.data.get('memory'))
        self.check_object_permissions(self.request, memory)
        serializer.save(memory=memory, file=self.request.data.get('file'))

class RetrieveVideoMemoryView(generics.RetrieveAPIView):
    http_method_names =['get']
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [VideoPermissions]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # For local development with Django's built-in server, you can use this:
        video_url = request.build_absolute_uri(instance.file.url)

        # In production, with AWS S3, you would use something like this instead:
        # video_url = generate_presigned_url(instance.file.name)

        return Response({"url": video_url})