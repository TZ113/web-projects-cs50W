from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import Max

from .models import *


class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'photo', 'category']
    
    
class NewBidForm(forms.Form):
    bid = forms.IntegerField(required=False)


class NewCommentForm(forms.Form):
    comment = forms.CharField(required=False, widget=forms.Textarea)


def index(request):
    listings = Listing.objects.all().exclude(active=False)
    
    for i in listings:
        cp = Bid.objects.filter(listing_id=i.id).aggregate(Max('bid'))
        if cp['bid__max']:
            i.price = cp['bid__max']
    return render(request, "auctions/index.html", {
        'listings': listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == 'POST':
        form = NewListingForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            print(request.user.username)
            l = Listing(maker_id = request.user.id, **form_data)
            l.save()
            return render(request, 'auctions/create_listing.html', {
                'message': 'Listing Successfully Created.',
                'form': NewListingForm()
            })
        else:
            return render(request, 'auctions/create_listing.html', {
                'form': form
            })
            
    
    return render(request, 'auctions/create_listing.html', {
        'form': NewListingForm()
    })
    

@login_required    
def listing(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
        print(listing)
    except Listing.DoesNotExist:
        return HttpResponseBadRequest('That can not be afforded.')
    cp = Bid.objects.filter(listing_id=listing_id).aggregate(Max('bid'))
    listing.last_bidder = '' 
    if cp['bid__max']:
        listing.price = cp['bid__max']
        bd = Bid.objects.filter(bid=cp['bid__max'], listing_id=listing_id)
        w = bd.first().bidder
        listing.last_bidder = w.username
    listing.total_bids = Bid.objects.filter(listing_id=listing_id).count()
    listing.comments = Comment.objects.filter(listing_id=listing_id)
    listing.in_watchlist = False
    wobj = Watchlist.objects.filter(user_id=request.user.id)
    if wobj.exists() and wobj[0].listings.filter(id=listing_id).exists():
        listing.in_watchlist = True  
    if request.method == "POST":
        bid_form = NewBidForm(request.POST)
        comment_form = NewCommentForm(request.POST)
        if bid_form.is_valid():
            bid_data = bid_form.cleaned_data
            if bid_data['bid']:
                if bid_data['bid'] > listing.price:
                    Bid.objects.create(listing_id=listing_id, bidder_id=request.user.id, bid=bid_data['bid'])
                    listing.price = bid_data['bid']
                    listing.total_bids += 1
                    listing.last_bidder = request.user.username
                    return render(request, 'auctions/listing.html', {
                        'listing': listing,
                        'bidform': NewBidForm(),
                        'message': 'Your bid is successfully Placed.',
                        'commentform': NewCommentForm(),
                        
                    })
                else:
                    return render(request, 'auctions/listing.html', {
                        'listing': listing,
                        'bidform': bid_form,
                        'message': f'Your Bid needs to be larger than {listing.price}gu.',
                        'commentform': NewCommentForm(),
                        
                    })
        else:
            return render(request, 'auctions/listing.html', {
                'listing': listing,
                'bidform': bid_form,
                'commentform': NewCommentForm()               
                })

        if comment_form.is_valid():
            comment_data = comment_form.cleaned_data
            if comment_data['comment']:
                Comment.objects.create(listing_id=listing_id, commenter_id=request.user.id, comment=comment_data['comment'])
                return render(request, 'auctions/listing.html', {
                    'listing': listing, 
                    'bidform': NewBidForm(),
                    'commentform': NewCommentForm()
                })
        else:
            return render(request, 'auctions/listing.html', {
                'listing': listing,
                'bidform': NewBidForm(),
                'commentform': comment_form
            })
                

    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'bidform': NewBidForm(), 
        'commentform': NewCommentForm(),
        
    })


@login_required
def close_auction(request, listing_id):
    Listing.objects.filter(pk=listing_id).update(active=False)
    return redirect('index')


@login_required
def add_remove_watchlist(request, listing_id):
        wobj = Watchlist.objects.filter(user_id=request.user.id)
        if wobj.exists() and wobj[0].listings.filter(id=listing_id).exists():
            wobj[0].listings.remove(listing_id)
            return redirect('listing', listing_id=listing_id)
        elif wobj.exists():
            wobj[0].listings.add(listing_id)
        else:
            new = Watchlist.objects.create(user_id=request.user.id)
            new.listings.add(listing_id)
        return redirect('listing', listing_id=listing_id)


@login_required
def watchlist(request):
    wobj = Watchlist.objects.filter(user_id=request.user.id)
    listings = []
    if wobj.exists() and wobj[0].listings.all().exists():
        listings = wobj[0].listings.all()
        return render(request, 'auctions/watchlist.html', {
            'listings': listings
        })
    else:
        return render(request, 'auctions/watchlist.html', {
            'message': 'You currently have no items in your Watchlist.'
        })
    
    
def categories(request, category):
    listings = Listing.objects.filter(category=category).exclude(active=False)
    if listings.exists():
        return render(request, 'auctions/categories.html', {
            'listings': listings
        })
    else:
        categories = Listing.cat_choices
        return render(request, 'auctions/categories.html', {
            'categories': categories
        })


def maker(request, maker_id):
    listings = Listing.objects.filter(maker_id=maker_id)
    if listings.exists():
        return render(request, 'auctions/maker.html', {
        'listings': listings
        })
    else:
        return HttpResponseBadRequest("None is the word")
    