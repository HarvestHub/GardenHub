from django.test import TestCase, Client
from django.urls import reverse
from gardenhub.factories import GardenFactory, GardenerFactory, CropFactory


class PlotUpdateViewTestCase(TestCase):

    def test_submit(self):
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
            reverse('plot-update', args=[plot.id]),
            {
                'garden': plot.garden.id,
                'title': plot.title,
                'gardener_emails': gardener.email,
                'crops': CropFactory().id
            }
        )

        self.assertRedirects(response, reverse('plot-list'))
