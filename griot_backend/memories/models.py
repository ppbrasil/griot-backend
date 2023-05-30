from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account

class Memory(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='memories')

    title = models.CharField(max_length=255)
    # allowed_access = models.ManyToManyField(User, related_name='accessible_memories')
    
    is_active = models.BooleanField(default=True, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.title

class Video(models.Model):
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='videos')
    file = models.FileField(upload_to='videos/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)