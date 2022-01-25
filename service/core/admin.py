from django.contrib import admin

# Register your models here.
from core.models import Widget, User

admin.site.register(User)
admin.site.register(Widget)
