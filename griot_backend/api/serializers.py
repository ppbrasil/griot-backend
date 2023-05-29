from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from rest_framework import serializers, exceptions
from profiles.models import Profile
from accounts.models import Account
from characters.models import Character
from memories.models import Memory, Video


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def validate_username(self, value):
        value = value.lower()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("the username already taken.")
        return value
    
    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already in use.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def create(self, validated_data):
        user = User(
            email=validated_data.get('email').lower(),
            username=validated_data.get('username').lower()
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
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

class AccountSerializer(serializers.ModelSerializer):
    owner_user = serializers.ReadOnlyField(source='owner_user.id')
    beloved_ones_profiles = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = '__all__'

    def get_beloved_ones_profiles(self, instance):
        # This method gets the Profile objects related to the 'beloved_ones' Users.
        profiles = Profile.objects.filter(user__in=instance.beloved_ones.all())
        return ProfileSerializer(profiles, many=True).data

    def update(self, instance, validated_data):
        if 'owner_user' in self.initial_data:
            raise exceptions.PermissionDenied("Updating owner_user field is not allowed.")
        if 'beloved_ones' in self.initial_data:
            raise exceptions.PermissionDenied("Updating beloved_ones field is not allowed.")
        
        return super().update(instance, validated_data)
    
class UserAccountSerializer(serializers.ModelSerializer):
    owned_accounts = AccountSerializer(many=True, read_only=True)
    beloved_accounts = AccountSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('owned_accounts', 'beloved_accounts')

class CharacterSerializer(serializers.ModelSerializer):
    memories = serializers.CharField(required=False)

    class Meta:
        model = Character
        fields = '__all__'

class MemorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Memory
        fields = '__all__'