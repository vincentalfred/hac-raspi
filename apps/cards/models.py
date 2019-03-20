from django.db import models
from django.contrib.auth.models import User
from apps.machines.models import Machine

class Card (models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	card_uid = models.CharField(max_length=8, db_index=True, unique=True)

	def __str__(self):
		return self.card_uid

class Unregistered_card (models.Model):
	machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
	card_uid = models.CharField(max_length=8, db_index=True, unique=True)
	tap_time = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.card_uid +", from:"+ self.machine