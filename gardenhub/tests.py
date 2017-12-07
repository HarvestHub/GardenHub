from django.test import TestCase
from django.contrib.auth import get_user_model, authenticate
from .models import Garden, Plot, Order


class UserTestCase(TestCase):
    """
    Test User model methods.
    """

    def setUp(self):
        # A garden and plot are first needed
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='Plot 1', garden=garden)

        # Create a gardener of a single plot
        self.gardener = get_user_model().objects.create_user(email='gardener@gardenhub.dev', password='gardener')
        plot.gardeners.add(self.gardener)

        # Create a garden manager of a single garden and no plots
        self.garden_manager = get_user_model().objects.create_user(email='garden_manager@gardenhub.dev', password='garden_manager')
        garden.managers.add(self.garden_manager)

        # Create a normal user who isn't assigned to anything
        self.normal_user = get_user_model().objects.create_user(email='normal_user@gardenhub.dev', password='normal_user')


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


    def test_get_orders(self):
        """ User.get_orders() """
        # TODO: Writing a test for this will be painful and I don't feel like it right now
        pass


    def test_is_garden_manager(self):
        """ User.is_garden_manager() """

        # Test a garden manager
        self.assertTrue(self.garden_manager.is_garden_manager())

        # Test *not* garden managers
        self.assertFalse(self.gardener.is_garden_manager())
        self.assertFalse(self.normal_user.is_garden_manager())


    def test_is_gardener(self):
        """ User.is_gardener() """

        # Test a gardener of a single plot
        self.assertTrue(self.gardener.is_gardener())

        # Test that a garden manager is also considered a gardener
        self.assertTrue(self.garden_manager.is_gardener())

        # Create and test a *not* gardener
        self.assertFalse(self.normal_user.is_gardener())


    def test_is_anything(self):
        """ User.is_anything() """

        # Test a normal user
        self.assertFalse(self.normal_user.is_anything())

        # Test a gardener and garden manager
        self.assertTrue(self.gardener.is_anything())
        self.assertTrue(self.garden_manager.is_anything())


    def test_has_open_orders(self):
        """ User.has_open_orders() """
        # TODO
        pass


    def test_can_edit_garden(self):
        """ User.can_edit_garden() """

        # Create garden
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')

        # Assign garden manager to garden
        garden_manager = get_user_model().objects.create_user(email='garden_manager2@gardenhub.dev', password='garden_manager2')
        garden.managers.add(garden_manager)

        # Test that the GM can edit the garden
        self.assertTrue(garden_manager.can_edit_garden(garden))

        # Test that a normal user can't edit the garden
        self.assertFalse(self.normal_user.can_edit_garden(garden))


    def test_can_edit_plot(self):
        """ User.can_edit_plot() """

        # Create plot
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='Plot 1', garden=garden)

        # Assign gardener to plot
        gardener = get_user_model().objects.create_user(email='gardener2@gardenhub.dev', password='gardener2')
        plot.gardeners.add(gardener)

        # Test that the gardener can edit the plot
        self.assertTrue(gardener.can_edit_plot(plot))

        # Test that a normal user can't edit the garden
        self.assertFalse(self.normal_user.can_edit_plot(plot))
