from django.db import models
from django.contrib.auth import get_user_model


class Profile(models.Model):
    class Sex(models.TextChoices):
        MALE = "Male"
        FEMALE = "Female"
        OTHER = "Other"

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(max_length=30, db_index=True)
    last_name = models.CharField(max_length=30)
    sex = models.CharField(max_length=6, choices=Sex, default=Sex.MALE)
    bio = models.TextField(max_length=500, blank=True)
    birthdate = models.DateField()
    avatar = models.ImageField(upload_to="profile_images", blank=True, null=True)
    cover_image = models.ImageField(upload_to="cover_images", blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
