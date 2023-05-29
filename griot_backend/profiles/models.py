from django.db import models
from django.contrib.auth.models import User

TIMEZONE_CHOICES = [
    ('UTC', 'Coordinated Universal Time'),
    ('America/New_York', 'Eastern Time (US & Canada)'),
    ('America/Chicago', 'Central Time (US & Canada)'),
    ('America/Denver', 'Mountain Time (US & Canada)'),
    ('America/Los_Angeles', 'Pacific Time (US & Canada)'),
    ('Europe/London', 'Greenwich Mean Time (GMT)'),
    ('Europe/Paris', 'Central European Time (CET)'),
    ('Asia/Kolkata', 'Indian Standard Time (IST)'),
    ('Australia/Sydney', 'Australian Eastern Standard Time (AEST)'),
    ('America/Sao_Paulo', 'Brasilia Time (BRT)'),
    ('Asia/Tokyo', 'Japan Standard Time (JST)'),
    ('Pacific/Auckland', 'New Zealand Standard Time (NZST)'),
]

LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('es', 'Spanish'),
    ('pt', 'Portuguese'),
]

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
]

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures', null=True, blank=True)
    name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=False)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=False)

    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} {self.last_name}'

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'