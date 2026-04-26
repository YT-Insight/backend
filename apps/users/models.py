from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from apps.common.models import BaseModel
from .manager import CustomUserManager

# Create your models here.

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    email = models.EmailField(unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    clerk_id = models.CharField(max_length=255, null=True, blank=True, unique=True, db_index=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email' # we will login with using email not username
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email:_<10}{self.first_name:_<10}{self.last_name:_<10}"
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"