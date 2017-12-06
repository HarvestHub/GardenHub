from django.test import TestCase
from django.contrib.auth import get_user_model, authenticate
from .models import Garden, Plot


class UserTestCase(TestCase):
    """
    Test User model methods.
    """

    def test_create_user(self):
        """ Create a user """

        # Create new user
        user = get_user_model().objects.create_user(email='test_create_user@gardenhub.dev', password='test_create_user')

        # Test that the user was saved
        self.assertEqual(user, get_user_model().objects.get(email='test_create_user@gardenhub.dev'))


    def test_user_auth(self):
        """ Ensure a user can authenticate """

        # Set variables
        user_email = 'test_user_auth@gardenhub.dev'
        user_password = 'test_user_auth'

        # Create new user
        user = get_user_model().objects.create_user(email=user_email, password=user_password)

        # Try to authenticate user
        auth_user = authenticate(email=user_email, password=user_password)

        # Ensure a match
        self.assertEqual(user, auth_user)


    def test_get_gardens(self):
        """ User.get_gardens() """

        # Create new User object
        user = get_user_model().objects.create_user(email='test_get_gardens@gardenhub.dev', password='test_get_gardens')

        # Create test Garden objects
        gardens = [
            Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776'),
            Garden.objects.create(title='Garden B', address='1001 Garden Rd, Philadelphia PA, 1776'),
            Garden.objects.create(title='Garden C', address='1010 Garden Rd, Philadelphia PA, 1776'),
            Garden.objects.create(title='Garden D', address='1011 Garden Rd, Philadelphia PA, 1776')
        ]

        # Create additional Gardens to make sure they *aren't* included in the results
        Garden.objects.create(title='Garden E', address='1100 Garden Rd, Philadelphia PA, 1776'),
        Garden.objects.create(title='Garden F', address='1101 Garden Rd, Philadelphia PA, 1776')

        # Assign user to gardens
        for garden in gardens:
            garden.managers.add(user)

        # Test that User.get_gardens() returns the correct result
        self.assertEqual(list(user.get_gardens()), gardens)


    def test_get_plots(self):
        """ User.get_plots() """

        # Create new User object
        user = get_user_model().objects.create_user(email='test_get_plots@gardenhub.dev', password='test_get_plots')

        # Create test Gardens
        gardens = [
            Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776'),
            Garden.objects.create(title='Garden B', address='1001 Garden Rd, Philadelphia PA, 1776'),
            Garden.objects.create(title='Garden C', address='1010 Garden Rd, Philadelphia PA, 1776'),
            Garden.objects.create(title='Garden D', address='1011 Garden Rd, Philadelphia PA, 1776')
        ]

        # Create test Plots
        plots = [
            Plot.objects.create(title='Plot 1', garden=gardens[0]),
            Plot.objects.create(title='Plot 2', garden=gardens[0]),
            Plot.objects.create(title='Plot 3', garden=gardens[1]),
            Plot.objects.create(title='Plot 4', garden=gardens[2])
        ]

        # Assign user to certain gardens and plots
        gardens[0].managers.add(user)
        plots[2].gardeners.add(user)

        # Test results
        result = [plots[0], plots[1], plots[2]]
        self.assertEqual(list(user.get_plots()), result)
