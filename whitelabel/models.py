from django.db import models
from django.contrib.auth.models import Group

# Create your models here.


class CompanyStyle(models.Model):
    user_group = models.ForeignKey(Group, on_delete=models.CASCADE)
    background_color_hex = models.CharField(default="#ffffff", max_length=7)
