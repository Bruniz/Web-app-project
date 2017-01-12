from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from YAAS.forms import *
from YAAS.models import *
import hashlib
from decimal import Decimal
from django.core.mail import send_mail
# Create your views here.

salt = "(rut&helga2016)" # Salt for creating an md5 hash to enable concurrency

def start(request):
    # Search all auctions (UC5)
    searchterm = request.GET.get('search')
    if searchterm != None:
        auctions = Auction.objects.filter(title__icontains=searchterm, banned=False)

    else:
        auctions = Auction.objects.filter(banned=False, active=True)

    return render(request, "auctions.html", {'auctions': auctions})

def signin(request):

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect('/yaas/')

    else:
        return HttpResponseRedirect('/login_error/')

def signout(request):
    logout(request)
    return HttpResponseRedirect('/yaas/')

def login_error(request):
    messages.add_message(request, messages.INFO, 'Wrong username or password, please try again!')
    return HttpResponseRedirect('/yaas/')

# Function for creating a new user account (UC1)
def register(request):

    form = RegistrationForm(request.POST)  # create form object

    if (request.method == "POST"):
        #form = UserCreationForm(request.POST)  # create form object

        if form.is_valid():  # Check if form is valid
            form.save()
            messages.add_message(request, messages.INFO, 'User created! Please login!')
            return HttpResponseRedirect('/yaas/')  # If succsessfull redirect to start page
        else:  # Invalid form
            #messages.add_message(request, messages.INFO, 'You entered something wrong, please try again')
            return render(request, 'register.html', {'form': form})
    else:  # GET method
        form = RegistrationForm()
        return render(request, 'register.html', {'form': form})

# Function for updating user information (UC2)
def edit_profile(request):
    if not request.user.is_authenticated():
        messages.add_message(request, messages.INFO, 'Log in to edit profile')
        return HttpResponseRedirect('/yaas/')
    else:
        form = UserForm(request.POST, instance=request.user)  # create form object
        if(request.method == "POST" and form.is_valid()):
            form.save()
            return HttpResponseRedirect('/yaas/')  # If succsessfull redirect to start page
        else:
            form = UserForm(instance=request.user)  # create form object
            return render(request, 'edit_profile.html', {'form': form})

# Method for updating user password (UC2)
def change_password(request):
    if not request.user.is_authenticated():
        messages.add_message(request, messages.INFO, 'Log in to change password')
        return HttpResponseRedirect('/yaas/')
    else:
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.add_message(request, messages.INFO, 'Password changed!')
            return HttpResponseRedirect('/yaas/')  # If succsessfull redirect to start page
        else:
            return render(request, 'change_password.html', {'form': form})

# Function for creating a new auction (UC3)
def create_auction(request):

    if not request.user.is_authenticated():
        messages.add_message(request, messages.INFO, 'Log in to add a blog')
        return HttpResponseRedirect('/yaas/')
    else:


        if request.method == "POST":
            form = CreateAuctionForm(data=request.POST)
            #DEBUGprint("debug1")
            if (form.is_valid()):
                auction = Auction()
                auction.title = request.POST["title"]
                auction.description = request.POST["description"]
                auction.deadline = request.POST["deadline"]
                auction.price = request.POST["price"]
                # active and banned are both set to 'False' by default in the model
                auction.seller = request.user
                #DEBUGprint (request.user)
                auction.email = request.user.email
                #DEBUGprint(auction.email)
                md5 = hashlib.md5(
                    (str(auction.title) + str(auction.description) + str(auction.deadline) + str(auction.price) + str(auction.seller.username) + salt).encode('utf-8'))
                auction.version =  md5.hexdigest() # Add the current version has to object

                return render(request, "confirm_auction.html",{'auction': auction})
            else: # Something was inputted incorrectly
                messages.add_message(request, messages.INFO, 'Something went wrong')
                return render(request, "create_auction.html", {'form': form} )
        else: # GET method
            form = CreateAuctionForm()
            return render(request, "create_auction.html", {'form': form})

# Confirm the new auction (UC3)
def confirm_auction(request):
    if not request.user.is_authenticated() :
        print('Not authenticated')
        messages.add_message(request, messages.INFO, 'Log in to add a blog')
        return HttpResponseRedirect('/yaas/')
    else:
        if request.method == "POST":
            print('POST')
            if'saveAuction' in request.POST:
                print('Action saves')
                auction = Auction()
                auction.title = request.POST["title"]
                auction.description = request.POST["description"]
                auction.deadline = request.POST["deadline"]
                auction.price = request.POST["price"]
                # active and banned are both set to 'False' by default in the model
                auction.active = True;
                auction.seller = request.user
                print(request.user)

                auction.email = request.user.email
                #DEBUGprint(auction.email)
                md5 = hashlib.md5(
                    (str(auction.title) + str(auction.description) + str(auction.deadline) + str(auction.price) + str(auction.seller.username) + salt).encode('utf-8'))
                auction.version = md5.hexdigest()  # Add the current version has to object

                auction.save()

                send_mail(
                    'New auction created',
                    'You you just created a new auction '+auction.title+
                    '. Here is a link you can use to edit the auction without logging in. '
                    'http://127.0.0.1:8000/edit/'+auction.version+
                    ' Note: The link will only be valid until someone places a bid or you edit the description.',
                    'info@yaas.com',
                    [auction.email],
                    fail_silently=False,
                    )

                messages.add_message(request, messages.INFO, 'The auction was saved')
                return HttpResponseRedirect('/yaas/')
            else:
                messages.add_message(request, messages.INFO, 'The auction was discarded')
                return HttpResponseRedirect('/yaas/')

        else: # GET method
            messages.add_message(request, messages.INFO, 'Not allowed')
            return HttpResponseRedirect('/yaas/')

def show_auction(request, id):

    form = BidForm()
    auction = Auction.objects.get(id=id)
    return render(request, "auction.html", {'form': form, 'auction': auction})


# Function for placing bids (UC6)
def place_bid(request, id):

    if request.user.is_authenticated(): # You must be logged in to place a bid

        if request.method == "POST": # Place a new bid

            form = BidForm(data=request.POST) # Form to fill in
            auction = Auction.objects.get(id=id)  # Get auction
            if form.is_valid() == False:
                return render(request, "auction.html", {'form': form, 'auction': auction})
            bid = BidObject() # New bid

            auction = Auction.objects.get(id=id) # Get auction
            user = request.user # Get user
            bid.auction = auction # Bind auction to bid
            bid.bidder = user # Bind user to bid
            bid.bid = Decimal(form.data['bid']) # Add the bid amount to bid ( the amount you raise with)

            # Optional soft deadlines for bid
            if timedelta(seconds=0) < auction.deadline - timezone.now() < timedelta(minutes=5): # Check if deadline will end within 5min
                auction.deadline += timedelta(minutes=5) # if so add 5 minutes to deadline
                messages.add_message(request, messages.INFO, 'You placed a bid within 5 minutes if deadline, deadline extended by 5 minutes')

            if auction.version != request.POST['version']: # Concurrency check
                messages.add_message(request, messages.INFO, 'Someone else placed a bid or edited the auction')
                return render(request, "auction.html", {'form': form, 'auction': auction}) # Display the form again

            #DEBUG
            print(auction != None)
            print(form.is_valid())
            print(user != auction.seller)
            print(auction.banned == False)
            print(auction.active)
            print(user)
            print(auction.seller)

            # You must bid on an auction which also is not your own and it needs to be acive and not banned
            if auction != None and form.is_valid() and user != auction.seller and auction.banned == False and auction.active:
                print('accept bid')
                if auction.bidobject_set.count() > 0: # If the bid is not the first bid
                    lastWinner = auction.bidobject_set.first().bidder
                    print('not first bid')
                    print(auction.bidobject_set.first().bidder)
                    if auction.bidobject_set.first().bidder != user: # You cannot bid if you are already winning
                        print('you are not winning.. yet')
                        auction.price += bid.bid # Add the bid to the price
                        bid.bid = auction.price # The bid is the bid amount + auction price
                        bid.save() # Save bid
                        auction.winner = bid.bidder.username # The one that is currently winning
                        md5 = hashlib.md5(
                            (str(auction.title) + str(auction.description) + str(auction.deadline) + str(
                                auction.price) + str(auction.seller.username) + salt).encode('utf-8'))
                        auction.version = md5.hexdigest()  # Add the current version has to object
                        auction.save() # Save auciton

                        send_mail( # Notify the seller and previous winner about the bid
                            'New bid',
                            'The auction ' + auction.title + ' got a new bid of ' + str(
                                auction.price) + '€ by ' + auction.winner,
                            'info@yaas.com',
                            [auction.seller.email, bid.bidder.email, lastWinner.email],
                            fail_silently=False,
                            )
                else: # The bid was the first bid
                    print('first bid')
                    auction.price += bid.bid  # Add the bid to the price
                    bid.bid = auction.price  # The bid is the bid amount + auction price
                    bid.save()  # Save bid
                    auction.winner = bid.bidder.username
                    md5 = hashlib.md5(
                        (str(auction.title) + str(auction.description) + str(auction.deadline) + str(
                            auction.price) + str(auction.seller.username) + salt).encode('utf-8'))
                    auction.version = md5.hexdigest()  # Add the current version has to object
                    auction.save()

                    send_mail( # Notify seller and bidder about the new bid
                        'New bid',
                        'The auction ' + auction.title + ' got a new bid of ' + str(
                            auction.price) + '€ by ' + auction.winner,
                        'info@yaas.com',
                        # TODO fix email get user object and their email. Both lastWinner and new winner
                        [auction.seller.email, bid.bidder.email],
                        fail_silently=False,
                        )

                return HttpResponseRedirect('/show_auction/' + str(id))

            return render(request, "auction.html", {'form': form, 'auction': auction})
        else:

            return HttpResponseRedirect('/show_auction/'+str(id))

    else:
        messages.add_message(request, messages.INFO, 'Please login to place bid')
        return HttpResponseRedirect('/yaas/')

# Seller can edit description of auction (UC4)
def edit_auction(request, id):

    if request.user.is_authenticated(): # You must be logged in
        if request.method == "POST":
            auction = Auction.objects.get(id=id) # Get the auction if a POST

            if auction.seller == request.user and auction != None: # You can only edit your own auction
                auction.description = request.POST['description'] # Set the new description
                md5 = hashlib.md5(
                    (str(auction.title) + str(auction.description) + str(auction.deadline) + str(
                        auction.price) + str(auction.seller.username) + salt).encode('utf-8'))
                auction.version = md5.hexdigest()  # Add the current version hash to object
                auction.save() # Save the edited auction
            return HttpResponseRedirect('/show_auction/'+str(auction.id))
        else:# GET request
            template = loader.get_template('edit_auction.html')
            context = {'auction': Auction.objects.get(id=id)}
            return HttpResponse(template.render(context, request)) # Render a form with auction details filled in
    else:
        messages.add_message(request, messages.INFO, 'Please login to edit auction') # Message to prompt login
        return HttpResponseRedirect('/yaas/')

# Admin can ban an auction (UC7)
def ban_auction(request, id):

    if request.user.is_superuser == True: # Only superuser can ban
        # Get auction and ban it
        auction = Auction.objects.get(id=id)
        auction.banned = True
        auction.save()
        # Get all the bidders email addresses
        bidderEmails = ''
        for bid in auction.bidobject_set.all(): # Loop through all bidders
            if bid.bidder.email not in bidderEmails: # No duplicates
                bidderEmails = bidderEmails+bid.bidder.email+', ' # Append all emails to a string

        send_mail( # Send the email to seller and all bidders
            'Auction banned',
            'The auction ' + auction.title + ' is now banned.',
            'info@yaas.com',
            [auction.seller.email, bidderEmails],
            fail_silently=False,
            )

        messages.add_message(request, messages.INFO, 'The auction was banned') # Let the admin know it succeeded
        return HttpResponseRedirect('/yaas/') # Redirect to start

# Optional requirement (UC3)
def edit(request, hash):

    #DEBUGprint(hash)

    if request.method == 'POST':
        auctions = Auction.objects.filter(version__exact=hash)# Find the requested auction
        auction = auctions.first() # Get the auction object
        auction.description = request.POST['description']  # Set the new description
        md5 = hashlib.md5(
            (str(auction.title) + str(auction.description) + str(auction.deadline) + str(
                auction.price) + str(auction.seller.username) + salt).encode('utf-8'))
        auction.version = md5.hexdigest()  # Add the current version hash to object
        auction.save()  # Save the edited auction
        return HttpResponseRedirect('/show_auction/' + str(auction.id)) # Show the newly edited auction

    else:
        template = loader.get_template('edit_hash.html') # Template for GET request
        auctions = Auction.objects.filter(version__exact=hash)  # Find the requested auction
        auction = auctions.first()  # Get the auction object
        #DEBUGprint(auction.title)
        context = {'auction': auction}
        return HttpResponse(template.render(context, request))  # Render a form with auction details filled in