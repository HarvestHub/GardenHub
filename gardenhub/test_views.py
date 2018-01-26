from django.test import TestCase, Client
from django.urls import reverse
from gardenhub.models import Plot
from gardenhub.factories import (
    GardenFactory, ActiveUserFactory, GardenerFactory, GardenManagerFactory,
    CropFactory
)


class PlotCreateViewTestCase(TestCase):

    def test_get(self):
        """ Ensure that the page can be accessed """
        client = Client()
        # Only GM's can access the page
        client.force_login(GardenManagerFactory())
        response = client.get(reverse('plot-create'))
        self.assertEqual(response.status_code, 200)

    def test_access(self):
        """ Only GM's can access the page """
        client = Client()
        # Normal users can't access
        client.force_login(ActiveUserFactory())
        response = client.get(reverse('plot-create'))
        self.assertEqual(response.status_code, 302)

    def test_post(self):
        """ Test submit under ideal conditions """
        client = Client()

        manager = GardenManagerFactory()
        garden = manager.get_gardens().first()
        client.force_login(manager)

        response = client.post(
            reverse('plot-create'), {
                'garden': garden.id,
                'title': '0',
                'gardener_emails': manager.email,
                'crops': CropFactory().id
            }
        )

        # Test status code
        self.assertRedirects(response, reverse('plot-list'))

        # Test that object was created
        self.assertTrue(Plot.objects.get(title=0))


class PlotUpdateViewTestCase(TestCase):

    def test_post(self):
        """ Test that the form submits """
        client = Client()

        gardener = GardenerFactory()
        plot = gardener.get_plots().first()
        client.force_login(gardener)

        # Add user to multiple gardens
        # https://github.com/HarvestHub/GardenHub/issues/88
        plot.garden.managers.add(gardener)
        GardenFactory(managers=[gardener])

        response = client.post(
            reverse('plot-update', args=[plot.id]), {
                'garden': plot.garden.id,
                'title': "New title",
                'gardener_emails': gardener.email,
                'crops': CropFactory().id
            }
        )

        # Ensure the correct response
        self.assertRedirects(response, reverse('plot-list'))

        # Check that the model updated
        plot.refresh_from_db()
        self.assertEqual(plot.title, "New title")
