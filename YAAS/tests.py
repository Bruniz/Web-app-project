from datetime import timezone, timedelta
from django.test import Client

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.test import TestCase
from .models import Auction
from .views import *
from django.contrib.messages.storage.fallback import FallbackStorage

# Test for UC3(TR2.1)
class TestUC3(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testUser', email='test@user.com', password='top_secret123')

    def test_create_auction(self):

        Auction.objects.create(title="Title", description="Description", deadline=timezone.now()+timedelta(hours=72),seller=self.user,price=1.00)
        request = self.factory.get('/show_auction/')
        request.user = self.user
        response = show_auction(request, '1')
        self.assertEqual(response.status_code, 200)  # OK
        auction = Auction.objects.all().filter(id=1).first()  # Find the requested auction
        self.assertEqual(Auction.objects.all().count(), 1)
        self.assertIsNotNone(auction)



    def test_post_auction(self):


        request = self.factory.post('/create_auction/', {'title': 'new auction', 'version':'5c0b8f9b381b197af51f697ff586542d',
                                                         'description': 'Much stuff', 'deadline': str(timezone.now()+timedelta(hours=73)),
                                                         'seller':self.user,'price': str(1.00)})
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = self.user
        response = create_auction(request)
        auction = Auction.objects.all().filter(title='new auction').first()  # Find the requested auction
        print(response)
        self.assertIsNone(auction)

        request2 = self.factory.post('/confirm_auction/',
                                     {'title': 'new auction', 'version': '5c0b8f9b381b197af51f697ff586542d',
                                      'description': 'Much stuff', 'deadline': str(timezone.now() + timedelta(hours=73)),
                                      'seller': self.user, 'price': str(1.00), 'saveAuction': 'saveAuction'})
        request2.user = self.user
        setattr(request2, 'session', 'session')
        messages = FallbackStorage(request2)
        setattr(request2, '_messages', messages)
        response = confirm_auction(request2)
        auctions = Auction.objects.filter(title='new auction')  # Find the requested auction
        auction = auctions.first()  # Get the auction object
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(auction)


# TEst for UC6 (TR2.2) and (TR2.3)
class TestUC6(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(
            username='testUser', email='test@user.com', password='top_secret123')
        self.user2 = User.objects.create_user(
            username='testUser2', email='test2@user.com', password='top_secret123')
        self.user3 = User.objects.create_user(
            username='testUser3', email='test2@user.com', password='top_secret123')
        Auction.objects.create(title="Title", description="Description", deadline=timezone.now() + timedelta(hours=72),
                               seller=self.user1, price=1.00, version="5c0b8f9b381b197af51f697ff586542d", active=True)
        Auction.objects.create(title="Title", description="Description", deadline=timezone.now() + timedelta(hours=72),
                               seller=self.user1, price=1.00, version="5c0b8f9b381b197af51f697ff586542b", active = True)
        Auction.objects.create(title="Title", description="Description", deadline=timezone.now() + timedelta(hours=72),
                               seller=self.user1, price=1.00, version="5c0b8f9b381b197af51f697ff586542c", active=True)
        Auction.objects.create(title="Title", description="Description", deadline=timezone.now() + timedelta(hours=72),
                               seller=self.user1, price=1.00, version="5c0b8f9b381b197af51f697ff586542a", active=True)

    # The seller should not be able to bid on own auction
    def test_own_bid(self):

        request = self.factory.post('/place_bid/', {'bid':str(3.00), 'version':'5c0b8f9b381b197af51f697ff586542d'})
        request.user = self.user1
        response = place_bid(request,1)
        print(response.status_code)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Auction.objects.get(id=1).price, 1.00) # Should not be 4.00

    # Normal bid by generic user which is not seller. Should be accepted
    def test_bid(self):

        request = self.factory.post('/place_bid/', {'bid':str(3.00), 'version':'5c0b8f9b381b197af51f697ff586542b'})
        request.user = self.user2
        response = place_bid(request, 2)
        self.assertEqual(response.status_code, 302) # Should be redirected on successful POST
        self.assertEqual(Auction.objects.get(id = 2).price, 4.00)


    # Test of bid concurrency (TR2.3) request1 is made first then request2 which will not succeed when the version has changed
    def test_concurrency(self):
        request1 = self.factory.post('/place_bid/', {'bid': str(3.00), 'version': '5c0b8f9b381b197af51f697ff586542c'})
        request1.user = self.user2
        resp = place_bid(request1, 3)
        self.assertEqual(resp.status_code, 302) # Redirect on successful post
        request2 = self.factory.post('/place_bid/', {'bid': str(5.00), 'version': '5c0b8f9b381b197af51f697ff586542c'})
        setattr(request2, 'session', 'session')
        messages = FallbackStorage(request2)
        setattr(request2, '_messages', messages)
        request2.user = self.user3
        response = place_bid(request2, 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Auction.objects.get(id=3).price, 4.00)

    # Bid under min bid limit should not change the value of the auction price
    def test_min_bid(self):
        request = self.factory.post('/place_bid/', {'bid': str(0.00999999), 'version': '5c0b8f9b381b197af51f697ff586542a'})
        request.user = self.user2
        response = place_bid(request, 4)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Auction.objects.get(id=4).price, 1.00)
