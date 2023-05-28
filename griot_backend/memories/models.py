from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account

class Memory(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='characters')

    title = models.CharField(max_length=255)
    allowed_access = models.ManyToManyField(User, related_name='accessible_memories')
    video = models.FileField(upload_to='memories/videos')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
