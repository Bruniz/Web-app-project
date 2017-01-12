
from django.forms import ModelForm, EmailField, SplitDateTimeWidget
from django.contrib.auth.models import User
from django.contrib.auth.forms import *
from django.core import validators
from django.utils import timezone
from _datetime import timedelta
from decimal import Decimal
from YAAS.models import *

class RegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class CreateAuctionForm(ModelForm):

    class Meta:

        model = Auction
        fields = ['title', 'description', 'deadline', 'price']

    def __init__(self, *args, **kwargs):
        super(CreateAuctionForm, self).__init__(*args, **kwargs)

        self.fields['price'] = forms.DecimalField(min_value=0.01, max_digits=8, decimal_places=2)

    def clean_deadline(self):

        deadline = self.cleaned_data['deadline']
        #DEBUGprint(deadline)
        today = timezone.now()
        #DEGUBprint(today)

        if deadline - today < timedelta(hours=72): # Check if the deadline is not within 72 hours of today

            raise forms.ValidationError("Minimum auction time of 72h")

        return deadline

    def clean_price(self):

        try:
            price = Decimal(self.cleaned_data['price'])
        except:
            raise forms.ValidationError("Incorrect input. Input a number")

        if (price < 0.009):
            raise forms.ValidationError("Minimum price is 0.01")

        return price


class BidForm(ModelForm):

    class Meta:
        model = BidObject
        fields = ['bid']

    def __init__(self, *args, **kwargs):
        super(BidForm, self).__init__(*args, **kwargs)

        self.fields['bid'] = forms.DecimalField(min_value=0.01, max_digits=8, decimal_places=2)

    def clean_bid(self):
        try:
            bid = Decimal(self.cleaned_data['bid'])

        except:
            raise forms.ValidationError("Incorrect input. Input a number")


        if(bid < 0.009):
            raise forms.ValidationError("Minimum bid is 0.01")

        return bid
