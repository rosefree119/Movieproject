from urllib import request

from django.shortcuts import render
from movieapp.models import Movie
from django.db.models import Q


# Create your views here.


def SearchResult(request):
    title = Movie.title
    query = None
    image = None
    if 'q' in request.GET:
        query = request.GET.get('q')
        title = Movie.objects.all().filter(Q(title__contains=query))
        return render(request, 'search.html', {'query': query, 'title': title, 'image': image})
