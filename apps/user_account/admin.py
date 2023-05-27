from django.contrib import admin

from .models import Billing, CustomUser

admin.site.register([Billing, CustomUser])