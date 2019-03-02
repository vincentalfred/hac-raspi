from django.db import models
from apps.machines.models import Machine

class Tap (models.Model):
	card_uid = models.CharField(max_length=20)
	machine = models.ForeignKey(Machine, on_delete=models.DO_NOTHING)
	tap_time = models.DateTimeField(auto_now=True)
	power_usage = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return self.card_uid + self.machine.id