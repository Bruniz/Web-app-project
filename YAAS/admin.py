from django.contrib import admin
from .models import Auction, BidObject
# Register your models here.
admin.site.register(Auction)
admin.site.register(BidObject)