from django.db import models
from django.contrib.auth.models import User

class Card (models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	card_uid = models.CharField(max_length=8, db_index=True, unique=True)
