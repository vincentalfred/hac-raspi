from django.db import models
from django.contrib.auth.models import User

class Profile (models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	nim = models.CharField(max_length=10, db_index=True, unique=True)
	name = models.CharField(max_length=200)	#set db_index=True
