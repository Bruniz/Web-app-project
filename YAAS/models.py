from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from _datetime import timedelta



class Auction(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=300)
    deadline = models.DateTimeField(help_text="Enter the date like: YYYY-MM-DD HH:MM", default=timezone.now()+timedelta(hours=72))
    version = models.CharField(max_length=50)
    active = models.BooleanField(default=False)
    banned = models.BooleanField(default=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    winner = models.CharField(max_length=100, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, help_text="Starting price", default=1.00)


    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['deadline']





class BidObject(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=8, decimal_places=2, default=1.00,
                              help_text="The amount you want to raise the bid with")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-bid']