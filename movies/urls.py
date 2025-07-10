from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('add/', views.movie_add, name='movie_add'),
    path('vote/<int:movie_id>/<str:vote_type>/', views.vote_view, name='vote'),
    path('users/<int:user_id>/movies/', views.user_movies, name='user_movies'),
]