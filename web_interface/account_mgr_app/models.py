from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __repr__(self):
        return("{}(user={},)".format(self.__class__.__name__, self.user))

    def __str__(self):
        return("Profile: " + str(self.user))


@receiver(post_save, sender = User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        print("new user")
        Profile.objects.create(user = instance)

@receiver(post_save, sender = User)
def save_user_profile(sender, instance, **kwargs):
    print("save_user_profile:",kwargs)
    print("save user")
    instance.profile.save()
