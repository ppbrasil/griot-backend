from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Account(models.Model):
    owner_user = models.ForeignKey(User, related_name="owned_accounts", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    beloved_ones = models.ManyToManyField(User, related_name="beloved_accounts", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
