from .settings import *

# Override settings for production environment
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'www.griot.me',
    'griot.me',
    'griot-load-balancer-1658910802.us-east-1.elb.amazonaws.com', 
    '18.206.170.241'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'griot-db',
        'USER': 'griotdb',
        'PASSWORD': 'dp_pass!',
        'HOST': 'griot-db.cubmeht6dhdd.us-east-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}