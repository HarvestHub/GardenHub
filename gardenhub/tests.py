from datetime import date, timedelta
from uuid import uuid4
from django.core import mail
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model, authenticate
from django.http import HttpResponse
from .models import Garden, Plot, Order
from gardenhub import decorators


def uuid_email():
    """ Returns a fake unique email address for testing """
    return "{}@gardenhub.dev".format(str(uuid4()))

def uuid_pass():
    """ Returns a fake unique password for testing """
    return str(uuid4())



class UserManagerTestCase(TestCase):
    """
    Test UserManager methods.
    """

    def test_get_or_invite_users(self):
        """ User.objects.test_get_or_invite_users() """

        # 4 email addresses
        emails = [uuid_email(), uuid_email(), uuid_email(), uuid_email()]

        # Turn the first 2 into real users to test the "get" functionality
        existing = [
            get_user_model().objects.create_user(email=emails[0], password=uuid_pass()),
            get_user_model().objects.create_user(email=emails[1], password=uuid_pass())
        ]

        # Create fake request
        inviter = get_user_model().objects.create_user(
            email=uuid_email(),
            password=uuid_pass(),
            first_name='Test',
            last_name='Test'
        )
        request = RequestFactory().get('/')
        request.user = inviter

        # Call function
        users = get_user_model().objects.get_or_invite_users(emails, request)

        # Test that each user is in the results
        for user in users:
            self.assertIn(user.email, emails)

        # Ensure that 2 emails were sent
        self.assertEqual(len(mail.outbox), 2)

        # Test the subject line of the first email
        self.assertEqual(mail.outbox[0].subject, 'Test Test invited you to join GardenHub')



class UserTestCase(TestCase):
    """
    Test User model methods.
    """

    def setUp(self):
        # A garden and plot are first needed
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='1', garden=garden)

        # Create a gardener of a single plot
        self.gardener = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        plot.gardeners.add(self.gardener)

        # Create a garden manager of a single garden and no plots
        self.garden_manager = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        garden.managers.add(self.garden_manager)

        # Create a normal user who isn't assigned to anything
        self.normal_user = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())


    def test_create_user(self):
        """ Create a user """

        # Save email address
        email = uuid_email()

        # Create new user with email
        user = get_user_model().objects.create_user(email=email, password=uuid_pass())

        # Test that the user was saved by its email
        self.assertEqual(user, get_user_model().objects.get(email=email))


    def test_inactivated_user_auth(self):
        """ Ensure that users can't authenticate by default """

        # Save email and password
        user_email = uuid_email()
        user_password = uuid_pass()

        # Create new user
        user = get_user_model().objects.create_user(
            email=user_email,
            password=user_password
        )

        # Try to authenticate user
        auth_user = authenticate(email=user_email, password=user_password)

        # Ensure that the user didn't authenticate
        self.assertEqual(auth_user, None)


    def test_activated_user_auth(self):
        """ Ensure an activated user can authenticate """

        # Save email and password
        user_email = uuid_email()
        user_password = uuid_pass()

        # Create new user
        user = get_user_model().objects.create_user(
            email=user_email,
            password=user_password,
            is_active=True # Users must be explicitly activated
        )

        # Try to authenticate user
        auth_user = authenticate(email=user_email, password=user_password)

        # Ensure a match
        self.assertEqual(user, auth_user)


    def test_get_gardens(self):
        """ User.get_gardens() """

        # Create new User object
        user = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())

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
        user = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())

        # Create test Gardens
        gardens = [
            Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776'),
            Garden.objects.create(title='Garden B', address='1001 Garden Rd, Philadelphia PA, 1776'),
            Garden.objects.create(title='Garden C', address='1010 Garden Rd, Philadelphia PA, 1776'),
            Garden.objects.create(title='Garden D', address='1011 Garden Rd, Philadelphia PA, 1776')
        ]

        # Create test Plots
        plots = [
            Plot.objects.create(title='1', garden=gardens[0]),
            Plot.objects.create(title='2', garden=gardens[0]),
            Plot.objects.create(title='3', garden=gardens[1]),
            Plot.objects.create(title='4', garden=gardens[2])
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
        plot = Plot.objects.create(title='1', garden=garden)

        # Create orders
        orders = [
            Order.objects.create(plot=plot, start_date=date(2017, 1, 1), end_date=date(2017, 1, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 2, 1), end_date=date(2017, 2, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 3, 1), end_date=date(2017, 3, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 4, 1), end_date=date(2017, 4, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 5, 1), end_date=date(2017, 5, 5), requester=self.normal_user)
        ]

        # Create user and assign it to the plot
        user = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        plot.gardeners.add(user)

        # Test orders
        self.assertEqual(list(user.get_orders()), orders)


    def test_get_peers(self):
        """ User.get_peers() """

        # Create test Gardens
        gardens = [
            Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776'),
            Garden.objects.create(title='Garden B', address='1001 Garden Rd, Philadelphia PA, 1776'),
            Garden.objects.create(title='Garden C', address='1010 Garden Rd, Philadelphia PA, 1776'),
            Garden.objects.create(title='Garden D', address='1011 Garden Rd, Philadelphia PA, 1776')
        ]

        # Create test Plots
        plots = [
            Plot.objects.create(title='1', garden=gardens[0]),
            Plot.objects.create(title='2', garden=gardens[2]),
            Plot.objects.create(title='3', garden=gardens[3]),
            Plot.objects.create(title='4', garden=gardens[3])
        ]

        # Create test Users
        users = [
            get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass()),
            get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass()),
            get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass()),
            get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass()),
            get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass()),
            get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass()),
            get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass()),
            get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass()),
            get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass()),
            get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass()),
        ]

        # Garden with 2 managers and 1 plot with 1 gardener
        gardens[0].managers.add(users[0], users[1])
        plots[0].gardeners.add(users[2])
        self.assertEqual(list(users[0].get_peers()), [users[1], users[2]])
        self.assertEqual(list(users[1].get_peers()), [users[0], users[2]])
        self.assertEqual(list(users[2].get_peers()), [])

        # Garden with 2 managers and no plots
        gardens[1].managers.add(users[3], users[4])
        self.assertEqual(list(users[3].get_peers()), [users[4]])
        self.assertEqual(list(users[4].get_peers()), [users[3]])

        # Garden with 0 managers and 1 plot with 2 gardeners
        gardens[2].managers.add(users[5], users[6])
        self.assertEqual(list(users[5].get_peers()), [users[6]])
        self.assertEqual(list(users[6].get_peers()), [users[5]])

        # Garden with 1 manager and 2 plots, each with 1 gardener
        gardens[3].managers.add(users[7])
        plots[2].gardeners.add(users[8])
        plots[3].gardeners.add(users[9])
        self.assertEqual(list(users[7].get_peers()), [users[8], users[9]])
        self.assertEqual(list(users[8].get_peers()), [])
        self.assertEqual(list(users[9].get_peers()), [])


    def test_get_picker_orders(self):
        """ User.get_picker_orders() """

        # Create garden, plot, and picker
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='1', garden=garden)
        picker = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        garden.pickers.add(picker)

        # Create active orders
        start_date = date.today() - timedelta(days=1)
        end_date = date.today() + timedelta(days=5)
        orders = [
            Order.objects.create(plot=plot, start_date=start_date, end_date=end_date, requester=picker),
            Order.objects.create(plot=plot, start_date=start_date, end_date=end_date, requester=picker),
            Order.objects.create(plot=plot, start_date=start_date, end_date=end_date, requester=picker)
        ]
        # Inactive orders, for good measure
        Order.objects.create(plot=plot, start_date=date.today()+timedelta(days=5), end_date=date.today()+timedelta(days=10), requester=picker)
        Order.objects.create(plot=plot, start_date=date.today()-timedelta(days=10), end_date=date.today()-timedelta(days=5), requester=picker)

        self.assertEqual(list(picker.get_picker_orders()), orders)


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


    def test_is_picker(self):
        """ User.is_picker() """

        # Test a normal user
        self.assertFalse(self.normal_user.is_anything())

        # Create garden and assign a picker
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        picker = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        garden.pickers.add(picker)

        # Test that the user is a picker
        self.assertTrue(picker.is_picker())


    def test_has_open_orders(self):
        """ User.has_open_orders() """

        # Create plot
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='1', garden=garden)

        # Create orders
        orders = [
            Order.objects.create(plot=plot, start_date=date(2017, 1, 1), end_date=date(2017, 1, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 2, 1), end_date=date(2017, 2, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 3, 1), end_date=date(2017, 3, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 4, 1), end_date=date(2017, 4, 5), requester=self.normal_user),
            Order.objects.create(plot=plot, start_date=date(2017, 5, 1), end_date=date(2017, 5, 5), requester=self.normal_user)
        ]

        # Create user and assign it to the plot
        user = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        plot.gardeners.add(user)

        # Test orders
        self.assertTrue(user.has_open_orders())
        self.assertFalse(self.normal_user.has_open_orders())


    def test_can_edit_garden(self):
        """ User.can_edit_garden() """

        # Create garden
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')

        # Assign garden manager to garden
        garden_manager = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        garden.managers.add(garden_manager)

        # Test that the GM can edit the garden
        self.assertTrue(garden_manager.can_edit_garden(garden))

        # Test that a normal user can't edit the garden
        self.assertFalse(self.normal_user.can_edit_garden(garden))


    def test_can_edit_plot(self):
        """ User.can_edit_plot() """

        # Create plot
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='1', garden=garden)

        # Test that the gardener can edit the plot
        gardener = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        plot.gardeners.add(gardener)
        self.assertTrue(gardener.can_edit_plot(plot))

        # Test that a garden manager can edit the plot
        garden_manager = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        garden.managers.add(garden_manager)
        self.assertTrue(garden_manager.can_edit_plot(plot))

        # Test that a normal user can't edit the plot
        self.assertFalse(self.normal_user.can_edit_plot(plot))


    def test_can_edit_order(self):
        """ User.can_edit_order() """

        # Create order
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='1', garden=garden)
        order = Order.objects.create(plot=plot, start_date=date(2017, 1, 1), end_date=date(2017, 1, 5), requester=self.normal_user)

        # Test that the gardener can edit the order
        gardener = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        plot.gardeners.add(gardener)
        self.assertTrue(gardener.can_edit_order(order))

        # Test that a garden manager can edit the order
        garden_manager = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        garden.managers.add(garden_manager)
        self.assertTrue(garden_manager.can_edit_order(order))

        # Test that a normal user can't edit the order
        self.assertFalse(self.normal_user.can_edit_order(order))


    def test_is_order_picker(self):
        """ User.is_order_picker() """

        # Create order
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='1', garden=garden)
        order = Order.objects.create(plot=plot, start_date=date(2017, 1, 1), end_date=date(2017, 1, 5), requester=self.normal_user)

        # Create picker
        picker = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        garden.pickers.add(picker)
        self.assertTrue(picker.is_order_picker(order))

        # Test that a normal user can't edit the order
        self.assertFalse(self.normal_user.is_order_picker(order))



class OrderManagerTestCase(TestCase):
    """
    Tests for the custom OrderManager
    """

    def test_get_complete_orders(self):
        """ Order.objects.get_complete_orders() """

        # Create garden, plot, and picker
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='1', garden=garden)
        picker = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        garden.pickers.add(picker)

        # Completed orders
        start_date = date.today() - timedelta(days=10)
        end_date = date.today() - timedelta(days=1)
        completed_orders = [
            Order.objects.create(plot=plot, start_date=start_date, end_date=end_date, requester=picker),
            Order.objects.create(plot=plot, start_date=start_date, end_date=end_date, requester=picker),
            Order.objects.create(plot=plot, start_date=start_date, end_date=end_date, requester=picker),
        ]

        # Incomplete orders
        incomplete_orders = [
            # Start date is greater than today
            Order.objects.create(plot=plot, start_date=date.today()+timedelta(days=5), end_date=date.today()+timedelta(days=10), requester=picker),
            # End date is greater than today
            Order.objects.create(plot=plot, start_date=date.today()-timedelta(days=10), end_date=date.today()+timedelta(days=5), requester=picker),
        ]

        # Test it
        result = Order.objects.get_complete_orders()
        for order in completed_orders:
            self.assertIn(order, list(result))
        for order in incomplete_orders:
            self.assertNotIn(order, list(result))


    def test_get_active_orders(self):
        """ Order.objects.get_active_orders() """

        # Create garden, plot, and picker
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        plot = Plot.objects.create(title='1', garden=garden)
        picker = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        garden.pickers.add(picker)

        # Active orders
        start_date = date.today() - timedelta(days=10)
        end_date = date.today() + timedelta(days=1)
        active_orders = [
            Order.objects.create(plot=plot, start_date=start_date, end_date=end_date, requester=picker),
            Order.objects.create(plot=plot, start_date=start_date, end_date=end_date, requester=picker),
            Order.objects.create(plot=plot, start_date=start_date, end_date=end_date, requester=picker),
        ]

        # Inactive orders
        inactive_orders = [
            # Start date is greater than today
            Order.objects.create(plot=plot, start_date=date.today()+timedelta(days=5), end_date=date.today()+timedelta(days=10), requester=picker),
            # End date is greater than today
            Order.objects.create(plot=plot, start_date=date.today()-timedelta(days=10), end_date=date.today()-timedelta(days=5), requester=picker),
        ]

        # Test it
        result = Order.objects.get_active_orders()
        for order in active_orders:
            self.assertIn(order, list(result))
        for order in inactive_orders:
            self.assertNotIn(order, list(result))


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
        self.normal_user = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())

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
        plot = Plot.objects.create(title='1', garden=garden)
        gardener = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        plot.gardeners.add(gardener)
        gardener_request = self.factory.get('/')
        gardener_request.user = gardener

        # Test a gardener request
        view = decorators.is_anything(self.generic_view)
        response = view(gardener_request)
        self.assertEqual(response.status_code, 200)

        # Create an instance of a GET request with a garden manager
        garden = Garden.objects.create(title='Garden A', address='1000 Garden Rd, Philadelphia PA, 1776')
        garden_manager = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
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
        plot = Plot.objects.create(title='1', garden=garden)

        # Test an unauthorized request
        response = plot_view(self.unauthorized_request, plot.id)
        self.assertEqual(response.status_code, 403)

        # Test a gardener on the plot
        gardener = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        plot.gardeners.add(gardener)
        gardener_request = self.factory.get('/')
        gardener_request.user = gardener
        response = plot_view(gardener_request, plot.id)
        self.assertEqual(response.status_code, 200)

        # Test a garden manager on the plot
        garden_manager = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
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
        plot = Plot.objects.create(title='1', garden=garden)

        # Test an unauthorized request
        response = garden_view(self.unauthorized_request, garden.id)
        self.assertEqual(response.status_code, 403)

        # Test a gardener on the plot
        gardener = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        plot.gardeners.add(gardener)
        gardener_request = self.factory.get('/')
        gardener_request.user = gardener
        response = garden_view(gardener_request, garden.id)
        self.assertEqual(response.status_code, 403)

        # Test a garden manager on the plot
        garden_manager = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
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
        plot = Plot.objects.create(title='1', garden=garden)
        order = Order.objects.create(plot=plot, start_date=date(2017, 1, 1), end_date=date(2017, 1, 5), requester=self.normal_user)

        # Test an unauthorized request
        response = order_view(self.unauthorized_request, order.id)
        self.assertEqual(response.status_code, 403)

        # Test a gardener on the order's plot
        gardener = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        plot.gardeners.add(gardener)
        gardener_request = self.factory.get('/')
        gardener_request.user = gardener
        response = order_view(gardener_request, order.id)
        self.assertEqual(response.status_code, 200)

        # Test a garden manager on the order's plot
        garden_manager = get_user_model().objects.create_user(email=uuid_email(), password=uuid_pass())
        garden.managers.add(garden_manager)
        garden_manager_request = self.factory.get('/')
        garden_manager_request.user = garden_manager
        response = order_view(garden_manager_request, order.id)
        self.assertEqual(response.status_code, 200)
