from django.contrib import admin
from .models import Category, Item, ExchangeRequest, UserProfile, Message

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(ExchangeRequest)
admin.site.register(UserProfile)
admin.site.register(Message)
