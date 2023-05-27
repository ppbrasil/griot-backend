from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from profiles.models import Profile


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User(
            email=validated_data.get('email', None),
            username=validated_data.get('username', None)
        )
        user.set_password(validated_data.get('password'))
        user.save()

        Profile.objects.create(user=user)

        return user


class AuthenticationSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        # Check that username and password are present
        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # Check that user is authenticated
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data
    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'