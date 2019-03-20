from django.db import models
from django.contrib.auth.models import User
from apps.machines.models import Machine_type

class Certification (models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	machine_type = models.ForeignKey(Machine_type, on_delete=models.CASCADE)
