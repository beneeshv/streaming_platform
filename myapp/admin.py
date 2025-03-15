from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserReg ,Category ,Video ,Watchlist

admin.site.register(UserReg)
admin.site.register(Category)
admin.site.register(Video)
admin.site.register(Watchlist)

