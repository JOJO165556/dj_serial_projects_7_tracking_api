from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT= "client", "Client"
        COURIER= "courier", "Courier"
        ADMIN= "admin", "Admin"

    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=Role.choices) #type: ignore

    def __str__(self):
        return f"{self.username} ({self.role})"
