from django.db import models
from django.contrib.auth.models import User
from apps.machines.models import Machine_type, Machine
from apps.cards.models import Card
from datetime import timedelta

class Usage (models.Model):
	user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
	machine_type = models.ForeignKey(Machine_type, on_delete=models.DO_NOTHING)
	machine = models.ForeignKey(Machine, on_delete=models.DO_NOTHING)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	total_usage = models.IntegerField()

class DailyUsage (models.Model):
	date = models.DateField(db_index=True)
	machine_type = models.ForeignKey(Machine_type, on_delete=models.CASCADE)
	total_usage = models.IntegerField(default=0)
	total_time = models.BigIntegerField(default=0)