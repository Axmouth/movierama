from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from .models import Movie, Vote
from movies.forms import MovieForm

User = get_user_model()

class VotingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', password='pass')
        self.other_user = User.objects.create_user(username='bob', password='pass')

        self.movie = Movie.objects.create(
            title="Interstellar",
            description="Great movie",
            user=self.other_user  # so 'alice' can vote
        )

        self.own_movie = Movie.objects.create(
            title="Self Movie",
            description="Can't vote on this",
            user=self.user
        )

    def test_user_can_like_movie(self):
        self.client.login(username='alice', password='pass')
        response = self.client.post(reverse('vote', args=[self.movie.id, 'like']))
        self.assertEqual(response.status_code, 302)  # Should redirect after voting
        self.assertEqual(response.url, reverse('movie_list'))  # Redirects to movie list
        self.assertEqual(Vote.objects.count(), 1)
        vote = Vote.objects.first()
        self.assertEqual(vote.vote_type, 'like')

    def test_user_can_switch_vote(self):
        self.client.login(username='alice', password='pass')
        self.client.post(reverse('vote', args=[self.movie.id, 'like']))
        self.client.post(reverse('vote', args=[self.movie.id, 'hate']))
        vote = Vote.objects.get(movie=self.movie, user=self.user)
        self.assertEqual(vote.vote_type, 'hate')

    def test_user_can_retract_vote(self):
        self.client.login(username='alice', password='pass')
        self.client.post(reverse('vote', args=[self.movie.id, 'like']))
        self.client.post(reverse('vote', args=[self.movie.id, 'like']))  # clicking again
        self.assertFalse(Vote.objects.filter(movie=self.movie, user=self.user).exists())

    def test_cannot_vote_on_own_movie(self):
        self.client.login(username='alice', password='pass')
        response = self.client.post(reverse('vote', args=[self.own_movie.id, 'like']))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('movie_list'))  # Redirects to movie list
        self.assertFalse(Vote.objects.filter(movie=self.own_movie, user=self.user).exists())
        self.assertEqual(Vote.objects.count(), 0)

    def test_unauthenticated_vote_redirects(self):
        response = self.client.post(reverse('vote', args=[self.movie.id, 'like']))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_invalid_vote_type_redirects(self):
        self.client.login(username='alice', password='pass')
        response = self.client.post(reverse('vote', args=[self.movie.id, 'spam']))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('movie_list'))
        self.assertEqual(Vote.objects.count(), 0)

    def test_vote_add_flash_message(self):
        self.client.login(username='alice', password='pass')
        response = self.client.post(reverse('vote', args=[self.movie.id, 'like']), follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Your vote was recorded" in str(m) for m in messages))

class MovieFormTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', password='pass')
        logged_in = self.client.login(username='alice', password='pass')
        assert logged_in, "Login failed in test setup"

    def test_valid_form(self):
        form_data = {'title': 'Test Movie', 'description': 'A test description'}
        form = MovieForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_fields(self):
        form = MovieForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('description', form.errors)

    def test_get_signup_form(self):
        self.client.logout()
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_invalid_form_returns_template(self):
        self.client.login(username='alice', password='pass')
        response = self.client.post(reverse('movie_add'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie_form.html')
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)

    @override_settings(DEBUG=True)
    def test_get_add_movie_form(self):
        self.client.login(username='alice', password='pass')
        response = self.client.get(reverse('movie_add'))
        print(response.status_code)  # Debugging output
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movie_form.html')

class MovieAddViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass')
        self.client = Client()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('movie_add'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_can_add_movie(self):
        self.client.login(username='alice', password='pass')
        response = self.client.post(reverse('movie_add'), {
            'title': 'New Movie',
            'description': 'Some description'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful add
        self.assertEqual(response.url, reverse('movie_list'))  # Redirects to movie list
        self.assertEqual(Movie.objects.count(), 1)
        movie = Movie.objects.first()
        self.assertEqual(movie.user, self.user)
        self.assertEqual(movie.title, 'New Movie')

class MovieListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass')
        self.other_user = User.objects.create_user(username='bob', password='pass')
        for i in range(3):
            Movie.objects.create(
                title=f"Movie {i}",
                description="desc",
                user=self.other_user
            )

    def test_movies_sorted_by_date(self):
        response = self.client.get(reverse('movie_list') + '?sort=date')
        self.assertEqual(response.status_code, 200)
        self.assertIn('movies', response.context)

    def test_movies_sorted_by_likes(self):
        # Create votes to affect sorting
        movie = Movie.objects.first()
        Vote.objects.create(movie=movie, user=self.user, vote_type=Vote.LIKE)
        response = self.client.get(reverse('movie_list') + '?sort=likes')
        self.assertEqual(response.status_code, 200)
        self.assertIn(movie, response.context['movies'])

    def test_movies_sorted_by_hates(self):
        movie = Movie.objects.first()
        Vote.objects.create(movie=movie, user=self.user, vote_type=Vote.HATE)
        response = self.client.get(reverse('movie_list') + '?sort=hates')
        self.assertEqual(response.status_code, 200)
        self.assertIn(movie, response.context['movies'])


class UserMovieViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='pass')
        self.other_user = User.objects.create_user(username='alice', password='pass')
        Movie.objects.create(title="Movie 1", description="...", user=self.user)
        Movie.objects.create(title="Movie 2", description="...", user=self.user)

    def test_user_movies_view_works(self):
        url = reverse('user_movies', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['movies']), 2)

    def test_invalid_user_404(self):
        response = self.client.get(reverse('user_movies', args=[999]))
        self.assertEqual(response.status_code, 404)

class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='pass')

    def test_login_redirects_to_home(self):
        response = self.client.post(reverse('login'), {
            'username': 'bob',
            'password': 'pass'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('movie_list'))

    def test_signup_creates_user(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)

    def test_signup_with_mismatched_passwords_fails(self):
        response = self.client.post(reverse('signup'), {
            'username': 'baduser',
            'password1': 'pass123',
            'password2': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # re-renders form
        form = response.context['form']
        self.assertIn('password2', form.errors)  # functional correctness
        self.assertContains(response, "didn’t match")  # UI correctness
        self.assertEqual(User.objects.filter(username='baduser').count(), 0)

    def test_authenticated_user_redirected_from_login(self):
        self.client.login(username='bob', password='pass')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('movie_list'))

    def test_authenticated_user_redirected_from_signup(self):
        self.client.login(username='bob', password='pass')
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('movie_list'))


class PaginationTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='alice', password='pass')
        for i in range(15):
            Movie.objects.create(title=f"Movie {i}", description="...", user=user)

    def test_first_page_has_movies(self):
        response = self.client.get(reverse('movie_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('page_obj' in response.context)
        self.assertEqual(len(response.context['movies']), 5)

    def test_second_page_has_movies(self):
        response = self.client.get(reverse('movie_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['movies']), 5)
