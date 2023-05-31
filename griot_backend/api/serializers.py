from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, smart_str 

from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator

from django.template.loader import render_to_string

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
    
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self):
        request = self.context.get('request')
        email = self.validated_data['email']
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            password_reset_url = request.build_absolute_uri(f'/user/password-reset-confirm/{uid}/{token}/')
            email_body = render_to_string('emails/password_reset_email.html', {
                'password_reset_url': password_reset_url,
                'username': user.username}
            )
            send_mail('Password Reset Request', email_body, 'admin@yourwebsite.com', [email])
        except User.DoesNotExist:
            pass

class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = smart_str (urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({'uidb64': ['Invalid value.']})

        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError({'token': ['Invalid value.']})

        password_validation.validate_password(data['new_password'], user)
        return data

    def save(self):
        uidb64 = self.data['uidb64']
        uid = smart_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        user.set_password(self.validated_data['new_password'])
        user.save()

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
    memories = serializers.PrimaryKeyRelatedField(queryset=Memory.objects.all(), many=True, required=False)

    class Meta:
        model = Character
        fields = '__all__'
        
class VideoSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(required=False)
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Video
        fields = '__all__'
        
    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.file.url)

class MemorySerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)
    id = serializers.ReadOnlyField(required=False)
    
    class Meta:
        model = Memory
        fields = ('id', 'account', 'title', 'videos')
