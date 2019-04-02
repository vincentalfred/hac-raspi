from django.db import models

class Machine_type (models.Model):
	machine_type_name = models.CharField(max_length=200, db_index=True, unique=True)

	def __str__(self):
		return self.machine_type_name

class Machine (models.Model):
	machine_type = models.ForeignKey(Machine_type, on_delete=models.CASCADE)
	machine_name = models.CharField(max_length=200)
	status = models.BooleanField(default=False)

	def __str__(self):
		return self.machine_name