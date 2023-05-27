from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, AuthenticationSerializer, ProfileSerializer
from profiles.models import Profile

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

class UpdateProfileView(generics.UpdateAPIView):
    http_method_names = ['patch']
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['pk']
        profile = Profile.objects.get(user__id=user_id)
        return profile
