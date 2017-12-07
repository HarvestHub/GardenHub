from datetime import date
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model, authenticate
from django.http import HttpResponse
from .models import Garden, Plot, Order
from gardenhub import decorators


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

        # Create plot
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='Plot 1', garden=garden)

        # Create orders
        orders = [
            Order.objects.create(plot=plot, start_date=date(2017, 1, 1), end_date=date(2017, 1, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 2, 1), end_date=date(2017, 2, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 3, 1), end_date=date(2017, 3, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 4, 1), end_date=date(2017, 4, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 5, 1), end_date=date(2017, 5, 5), requester=self.normal_user)
        ]

        # Create user and assign it to the plot
        user = get_user_model().objects.create_user(email='test_get_orders@gardenhub.dev', password='test_get_orders')
        plot.gardeners.add(user)

        # Test orders
        self.assertEqual(list(user.get_orders()), orders)


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

        # Create plot
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='Plot 1', garden=garden)

        # Create orders
        orders = [
            Order.objects.create(plot=plot, start_date=date(2017, 1, 1), end_date=date(2017, 1, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 2, 1), end_date=date(2017, 2, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 3, 1), end_date=date(2017, 3, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 4, 1), end_date=date(2017, 4, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 5, 1), end_date=date(2017, 5, 5), requester=self.normal_user)
        ]

        # Create user and assign it to the plot
        user = get_user_model().objects.create_user(email='test_has_open_orders@gardenhub.dev', password='test_has_open_orders')
        plot.gardeners.add(user)

        # Test orders
        self.assertTrue(user.has_open_orders())
        self.assertFalse(self.normal_user.has_open_orders())


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

        # Test that the gardener can edit the plot
        gardener = get_user_model().objects.create_user(email='gardener2@gardenhub.dev', password='gardener2')
        plot.gardeners.add(gardener)
        self.assertTrue(gardener.can_edit_plot(plot))

        # Test that a garden manager can edit the plot
        garden_manager = get_user_model().objects.create_user(email='test_can_edit_plot_garden_manager@gardenhub.dev', password='test_can_edit_plot_garden_manager')
        garden.managers.add(garden_manager)
        self.assertTrue(garden_manager.can_edit_plot(plot))

        # Test that a normal user can't edit the plot
        self.assertFalse(self.normal_user.can_edit_plot(plot))


    def can_edit_order(self):
        """ User.can_edit_order() """

        # Create order
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='Plot 1', garden=garden)
        order = Order.objects.create(plot=plot, start_date=date(2017, 1, 1), end_date=date(2017, 1, 5), requester=self.normal_user)

        # Test that the gardener can edit the order
        gardener = get_user_model().objects.create_user(email='can_edit_order_gardener@gardenhub.dev', password='can_edit_order_gardener')
        plot.gardeners.add(gardener)
        self.assertTrue(gardener.can_edit_order(order))

        # Test that a garden manager can edit the order
        garden_manager = get_user_model().objects.create_user(email='can_edit_order_garden_manager@gardenhub.dev', password='can_edit_order_garden_manager')
        garden.managers.add(garden_manager)
        self.assertTrue(garden_manager.can_edit_order(order))

        # Test that a normal user can't edit the order
        self.assertFalse(self.normal_user.can_edit_order(order))



class DecoratorTestCase(TestCase):
    """
    Test the functions in decorators.py
    """

    def setUp(self):
        # Create a basic view for testing auth decorators on
        def generic_view(request):
            return HttpResponse()
        self.generic_view = generic_view

        # Create a normal user who isn't assigned to anything
        self.normal_user = get_user_model().objects.create_user(email='normal_user2@gardenhub.dev', password='normal_user2')

        # Faking requests
        self.factory = RequestFactory()

        # Create an instance of a GET request with a normal user
        self.unauthorized_request = self.factory.get('/')
        self.unauthorized_request.user = self.normal_user


    def test_is_anything(self):
        """ decorators.is_anything() """

        # Test an unauthorized request
        view = decorators.is_anything(self.generic_view)
        response = view(self.unauthorized_request)
        self.assertEqual(response.status_code, 403)

        # Create an instance of a GET request with a gardener
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='Plot 1', garden=garden)
        gardener = get_user_model().objects.create_user(email='gardener3@gardenhub.dev', password='gardener3')
        plot.gardeners.add(gardener)
        gardener_request = self.factory.get('/')
        gardener_request.user = gardener

        # Test a gardener request
        view = decorators.is_anything(self.generic_view)
        response = view(gardener_request)
        self.assertEqual(response.status_code, 200)

        # Create an instance of a GET request with a garden manager
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        garden_manager = get_user_model().objects.create_user(email='test_is_anything_garden_manager@gardenhub.dev', password='test_is_anything_garden_manager')
        garden.managers.add(garden_manager)
        garden_manager_request = self.factory.get('/')
        garden_manager_request.user = garden_manager

        # Test a gardener request
        view = decorators.is_anything(self.generic_view)
        response = view(garden_manager_request)
        self.assertEqual(response.status_code, 200)


    def test_can_edit_plot(self):
        """ decorators.can_edit_plot() """

        # Create a test view
        @decorators.can_edit_plot
        def plot_view(request, plotId):
            return HttpResponse()

        # Create a plot
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='Plot 1', garden=garden)

        # Test an unauthorized request
        response = plot_view(self.unauthorized_request, plot.id)
        self.assertEqual(response.status_code, 403)

        # Test a gardener on the plot
        gardener = get_user_model().objects.create_user(email='test_can_edit_plot_gardener@gardenhub.dev', password='test_can_edit_plot_gardener')
        plot.gardeners.add(gardener)
        gardener_request = self.factory.get('/')
        gardener_request.user = gardener
        response = plot_view(gardener_request, plot.id)
        self.assertEqual(response.status_code, 200)

        # Test a garden manager on the plot
        garden_manager = get_user_model().objects.create_user(email='test_can_edit_plot_garden_manager@gardenhub.dev', password='test_can_edit_plot_garden_manager')
        garden.managers.add(garden_manager)
        garden_manager_request = self.factory.get('/')
        garden_manager_request.user = garden_manager
        response = plot_view(garden_manager_request, plot.id)
        self.assertEqual(response.status_code, 200)


    def test_can_edit_garden(self):
        """ decorators.can_edit_garden() """

        # Create a test view
        @decorators.can_edit_garden
        def garden_view(request, gardenId):
            return HttpResponse()

        # Create a plot
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='Plot 1', garden=garden)

        # Test an unauthorized request
        response = garden_view(self.unauthorized_request, garden.id)
        self.assertEqual(response.status_code, 403)

        # Test a gardener on the plot
        gardener = get_user_model().objects.create_user(email='test_can_edit_garden_gardener@gardenhub.dev', password='test_can_edit_garden_gardener')
        plot.gardeners.add(gardener)
        gardener_request = self.factory.get('/')
        gardener_request.user = gardener
        response = garden_view(gardener_request, garden.id)
        self.assertEqual(response.status_code, 403)

        # Test a garden manager on the plot
        garden_manager = get_user_model().objects.create_user(email='test_can_edit_garden_garden_manager@gardenhub.dev', password='test_can_edit_garden_garden_manager')
        garden.managers.add(garden_manager)
        garden_manager_request = self.factory.get('/')
        garden_manager_request.user = garden_manager
        response = garden_view(garden_manager_request, garden.id)
        self.assertEqual(response.status_code, 200)


    def test_can_edit_order(self):
        """ decorators.can_edit_order() """

        # Create a test view
        @decorators.can_edit_order
        def order_view(request, orderId):
            return HttpResponse()

        # Create an order
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='Plot 1', garden=garden)
        order = Order.objects.create(plot=plot, start_date=date(2017, 1, 1), end_date=date(2017, 1, 5), requester=self.normal_user)

        # Test an unauthorized request
        response = order_view(self.unauthorized_request, order.id)
        self.assertEqual(response.status_code, 403)

        # Test a gardener on the order's plot
        gardener = get_user_model().objects.create_user(email='test_can_edit_order_gardener@gardenhub.dev', password='test_can_edit_order_gardener')
        plot.gardeners.add(gardener)
        gardener_request = self.factory.get('/')
        gardener_request.user = gardener
        response = order_view(gardener_request, order.id)
        self.assertEqual(response.status_code, 200)

        # Test a garden manager on the order's plot
        garden_manager = get_user_model().objects.create_user(email='test_can_edit_order_garden_manager@gardenhub.dev', password='test_can_edit_order_garden_manager')
        garden.managers.add(garden_manager)
        garden_manager_request = self.factory.get('/')
        garden_manager_request.user = garden_manager
        response = order_view(garden_manager_request, order.id)
        self.assertEqual(response.status_code, 200)
