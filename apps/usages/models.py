from django.db import models
from django.contrib.auth.models import User
from apps.machines.models import Machine_type, Machine
from apps.cards.models import Card

# class Tap (models.Model):
# 	card = models.ForeignKey(Card, on_delete=models.DO_NOTHING)
# 	machine = models.ForeignKey(Machine, on_delete=models.DO_NOTHING)
# 	tap_time = models.DateTimeField()
# 	power_usage = models.IntegerField(null=True, blank=True)

class Usage (models.Model):
	user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
	machine_type = models.ForeignKey(Machine_type, on_delete=models.DO_NOTHING)
	machine = models.ForeignKey(Machine, on_delete=models.DO_NOTHING)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	total_usage = models.IntegerField()
