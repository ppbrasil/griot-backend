from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            return super().authenticate_credentials(key)
        except AuthenticationFailed as e:
            # Handle the invalid token error here
            raise AuthenticationFailed('Invalid token', code=401)
