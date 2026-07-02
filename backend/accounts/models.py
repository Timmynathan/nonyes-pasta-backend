from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True, help_text="Delivery address within Lagos")
    is_subscribed_newsletter = models.BooleanField(default=False)
    loyalty_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.username
