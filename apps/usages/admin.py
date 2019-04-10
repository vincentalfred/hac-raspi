from django.contrib import admin
from .models import Usage, DailyUsage

admin.site.register(Usage)
admin.site.register(DailyUsage)