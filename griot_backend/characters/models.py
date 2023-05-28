from django.db import models
from accounts.models import Account
from memories.models import Memory

class Character(models.Model):
    RELATIONSHIP_CHOICES = (
        ('family', 'Family'),
        ('friend', 'Friend'),
        ('other', 'Other'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='characters')
    memories = models.ManyToManyField(Memory, related_name='characters')

    name = models.CharField(max_length=255)
    picture = models.ImageField(upload_to='character/pictures', null=True, blank=True)
    relationship = models.CharField(max_length=10, choices=RELATIONSHIP_CHOICES, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name