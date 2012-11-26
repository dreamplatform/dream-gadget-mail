
from django.contrib.auth.models import User
from django.db import models

class Auth(models.Model):
  token = models.CharField(max_length=100)
  user = models.ForeignKey(User)