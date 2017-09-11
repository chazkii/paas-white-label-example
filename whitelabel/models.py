import uuid

from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class Company(models.Model):
    name = models.CharField(max_length=256)
    uiud = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name


class CompanyAdmin(models.Model):
    company = models.ForeignKey(Company, related_name='+')
    user = models.ForeignKey(User, related_name='+')

    def __str__(self):
        return "%s : %s" % (self.user.username, self.company.name)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, null=True, related_name='+')
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return "%s <%s>" % (self.user.username, self.user.email)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

