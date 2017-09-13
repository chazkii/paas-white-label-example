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


# This model allows for multiple admins per company
class CompanyAdmin(models.Model):
    company = models.ForeignKey(Company, related_name='+')
    user = models.ForeignKey(User, related_name='+')

    def __str__(self):
        return "%s : %s" % (self.user.username, self.company.name)


# We create a profile model as a non-invasive way of extending the default
# User model. More mentioned in the official docs here:
# https://docs.djangoproject.com/en/1.11/topics/auth/customizing/#extending-the-existing-user-model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, null=True, related_name='+')

    def __str__(self):
        return "%s <%s>" % (self.user.username, self.user.email)


# Leverages [Django signals](https://docs.djangoproject.com/en/1.11/topics/signals)
# to automatically create a profile instance everytime a user instance is created.
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

