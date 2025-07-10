from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404
from .forms import MovieForm
from .models import Movie, Vote
from .services import get_sorted_movies

class CustomLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('movie_list')
        return super().dispatch(request, *args, **kwargs)

def movie_list(request):
    sort = request.GET.get("sort", "date")
    movies = get_sorted_movies(sort=sort, user_id=None, current_user=request.user)

    paginator = Paginator(movies, 5)  # Show 5 movies per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "movie_list.html", {
        "page_obj": page_obj,
        "movies": page_obj.object_list,
        "sort": sort,
    })

def user_movies(request, user_id):
    try:
        target_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404("User not found")

    sort = request.GET.get("sort", "date")
    movies = get_sorted_movies(sort=sort, user_id=user_id, current_user=request.user)

    paginator = Paginator(movies, 5)  # Show 5 movies per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "movie_list.html", {
        "page_obj": page_obj,
        "movies": page_obj.object_list,
        "filter_user": target_user,
        "sort": sort,
    })

@login_required
def movie_add(request):
    if request.method != 'POST':
        return render(request, 'movie_form.html', {'form': MovieForm()})

    form = MovieForm(request.POST)
    if not form.is_valid():
        return render(request, 'movie_form.html', {'form': form})

    movie = form.save(commit=False)
    movie.user = request.user
    movie.save()
    messages.success(request, "Movie submitted successfully.")
    return redirect('movie_list')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('movie_list')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def vote_view(request, movie_id, vote_type):
    if vote_type not in [Vote.LIKE, Vote.HATE]:
        return redirect('movie_list')

    movie = get_object_or_404(Movie, pk=movie_id)

    # Prevent voting on own movie
    if movie.user == request.user:
        return redirect('movie_list')

    vote, created = Vote.objects.get_or_create(user=request.user, movie=movie)

    if not created:
        if vote.vote_type == vote_type:
            vote.delete()  # Retract vote
            messages.success(request, "Your vote was removed.")
        else:
            vote.vote_type = vote_type  # Switch vote
            vote.save()
            messages.success(request, "Your vote was updated.")
    else:
        vote.vote_type = vote_type
        vote.save()
        messages.success(request, "Your vote was recorded.")

    return redirect('movie_list')
