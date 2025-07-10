from django.db.models import Count, Q
from movies.models import Movie, Vote

def get_sorted_movies(sort="date", user_id=None, current_user=None):
    qs = Movie.objects.all().select_related("user").prefetch_related("votes")

    if user_id:
        qs = qs.filter(user__id=user_id)

    # Annotate vote counts
    qs = qs.annotate(
        likes_count=Count('votes', filter=Q(votes__vote_type=Vote.LIKE)),
        hates_count=Count('votes', filter=Q(votes__vote_type=Vote.HATE))
    )

    # Apply sorting
    if sort == "likes":
        qs = qs.order_by('-likes_count', '-date_added')
    elif sort == "hates":
        qs = qs.order_by('-hates_count', '-date_added')
    else:
        qs = qs.order_by('-date_added')

    movies = list(qs)

    # Attach user's vote to each movie
    if current_user and current_user.is_authenticated:
        vote_map = {
            v.movie_id: v.vote_type
            for v in Vote.objects.filter(user=current_user, movie__in=movies)
        }
        for m in movies:
            m.user_vote = vote_map.get(m.id)

    return movies

