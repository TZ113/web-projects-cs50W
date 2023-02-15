from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.contrib.auth.decorators import login_required

from .models import User, Post


def index(request):
    posts = Post.objects.all().order_by('-time')
    for post in posts:
        post.current_user_likes = False
        post.total_likes = post.likes.all().count()
        if request.user in post.likes.all():
            post.current_user_likes = True
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        'posts': posts,
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":

        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def post(request):
    if request.method == "POST":
        new_post = request.POST['post']
        if new_post == '':
            return JsonResponse({"error": "post something to post something"}, status=400)
        Post.objects.create(poster=request.user, post=new_post)
        
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get('post') is not None and data.get('post_id') is not None:   
            if data['post'] == '':
                return JsonResponse({"error": "post something to post something"}, status=403)
            Post.objects.filter(pk=data['post_id']).update(post=data['post'])
            return HttpResponse(status=204)
            
        elif data.get('post_id') is not None:
            p = Post.objects.get(id=data['post_id'])
            if request.user in p.likes.all():
                p.likes.remove(request.user)
            else:
                p.likes.add(request.user)
            likes = p.likes.all().count()
            
            return JsonResponse({"likes": likes})
        else:
            return JsonResponse({"error": "POST or PUT request required"}, status=400)
    
    return redirect('index')


def profiles(request, id):
    if request.method == "PUT":
        if id in [i.id for i in request.user.followings.all()]:
            request.user.followings.remove(User.objects.get(id=id))
            User.objects.get(id=id).followers.remove(request.user)
        else:
            request.user.followings.add(User.objects.get(id=id))
            User.objects.get(id=id).followers.add(request.user)

    posts = list(Post.objects.filter(poster_id=id).order_by('-time'))
    followings = User.objects.get(id=id).followings.all().count()
    followers = User.objects.get(id=id).followers.all().count()
    username = User.objects.get(id=id).username
    
    current_user_following = False
    if request.user in User.objects.get(id=id).followers.all():
         current_user_following = True

    for post in posts:
        post.current_user_likes = False
        post.total_likes = post.likes.all().count()
        if request.user in post.likes.all():
            post.current_user_likes = True
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    return render(request, 'network/profiles.html', {
        'id': id,
        'username': username,
        'posts': posts,
        'followers': followers,
        'followings': followings,
        'current_user_following': current_user_following
    })
    

@login_required
def following(request):
    posts = []
    for user in request.user.followings.all():
        posts += Post.objects.filter(poster=user)

    posts = sorted(posts, key=lambda x:x.time, reverse=True)
    print(posts)
    for post in posts:
        post.current_user_likes = False
        post.total_likes = post.likes.all().count()
        if request.user in post.likes.all():
            post.current_user_likes = True
            
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    return render(request, "network/following.html", {
        'posts': posts,
    })

