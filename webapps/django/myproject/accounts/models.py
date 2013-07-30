from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.ForeignKey(User, unique=True)
	zip_code = models.IntegerField(max_length=10, blank=True)

# Create your models here.
