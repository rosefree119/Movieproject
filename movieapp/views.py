from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User, Group
from .forms import SignUpForm, AddMovieForm, LoginForm, AddRatingForm
from .models import Movie, Rating
from django.contrib import messages
import pandas as pd
from math import sqrt
import numpy as np
# import matplotlib.pyplot as plt
from math import ceil
from django.conf import settings
from django.core.mail import send_mail


# Create your views here.

def filterMovieByGenre():
    # filtering by genres
    allMovies = []
    genresMovie = Movie.objects.values('genres', 'id')
    genres = {item["genres"] for item in genresMovie}
    for genre in genres:
        movie = Movie.objects.filter(genres=genre)
        print(movie)
        n = len(movie)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allMovies.append([movie, range(1, nSlides), nSlides])
    params = {'allMovies': allMovies}
    return params


def signup(request):
    if not request.user.is_authenticated:
        if request.user == 'POST':


            fm = SignUpForm(request.POST)
            if fm.is_valid():
                user = fm.save()
                group = Group.objects.get(name='Editor')
                user.groups.add(group)
                messages.success(request, 'Account Created Successfully!!!')
                uname = request.POST.get['username']

                email = request.POST.get["email"]

                user = User.objects.create_user(
                    username=uname,

                    email=email
                )
                login(request, user)

                subject = 'welcome to Movie Recommendation App'
                message = f'Hi {user.username}, thank you for registering in Movie Recommendation App.'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email, ]
                send_mail(subject, message, email_from, recipient_list)
                return redirect('/dashboard/')

        else:
            if not request.user.is_authenticated:
                fm = SignUpForm()
        return render(request, 'signup.html', {'form': fm})
    else:
        return HttpResponseRedirect('/home/')


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            fm = LoginForm(request=request, data=request.POST)
            if fm.is_valid():
                uname = fm.cleaned_data['username']
                upass = fm.cleaned_data['password']
                user = authenticate(username=uname, password=upass)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Logged in Successfully!!')
                    return HttpResponseRedirect('/dashboard/')
        else:
            fm = LoginForm()
        return render(request, 'login.html', {'form': fm})
    else:
        return HttpResponseRedirect('/dashboard/')


def home(request):
    params = filterMovieByGenre()

    return render(request, 'home.html', params)


def addmovie(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fm = AddMovieForm(request.POST, request.FILES)
            if fm.is_valid():
                fm.save()
                messages.success(request, 'Movie Added Successfully!!!')
        else:
            fm = AddMovieForm()
        return render(request, 'addmovie.html', {'form': fm})
    else:
        return HttpResponseRedirect('/login/')


def dashboard(request):
    if request.user.is_authenticated:
        params = filterMovieByGenre()
        params['user'] = request.user
        if request.method == 'POST':
            userid = request.POST.get('userid')
            movieid = request.POST.get('movieid')
            movie = Movie.objects.all()
            u = User.objects.get(pk=userid)
            m = Movie.objects.get(pk=movieid)
            rfm = AddRatingForm(request.POST)
            params['rform'] = rfm
            if rfm.is_valid():
                rat = rfm.cleaned_data['rating']
                count = Rating.objects.filter(user=u, movie=m).count()
                if (count > 0):
                    messages.warning(request, 'You have already submitted your review!!')
                    return render(request, 'dashboard.html', params)
                action = Rating(user=u, movie=m, rating=rat)
                action.save()
                messages.success(request, 'You have submitted' + ' ' + rat + ' ' + "star")
            return render(request, 'dashboard.html', params)
        else:

            rfm = AddRatingForm()
            params['rform'] = rfm
            movie = Movie.objects.all()
            return render(request, 'dashboard.html', params)
    else:
        return HttpResponseRedirect('/login/')


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect('/login/')


def profile(request):
    if request.user.is_authenticated:

        r = Rating.objects.filter(user=request.user.id)
        totalReview = 0
        for item in r:
            totalReview += int(item.rating)

        totalwatchedmovie = Rating.objects.filter(user=request.user.id).count()
        return render(request, 'profile.html', {'totalReview': totalReview, 'totalwatchedmovie': totalwatchedmovie})
    else:
        return HttpResponseRedirect('/login/')
