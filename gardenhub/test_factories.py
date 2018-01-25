from django.test import TestCase
from factory import Faker
from gardenhub.factories import (
    CropFactory,
    GardenFactory,
    PlotFactory,
    OrderFactory,
    PickFactory,
    ActiveUserFactory,
    GardenerFactory,
    PickerFactory
)


class CropFactoryTestCase(TestCase):
    def test_create(self):
        """ Test creation """
        self.assertTrue(CropFactory())


class GardenFactoryTestCase(TestCase):
    def test_create(self):
        """ Test creation """
        self.assertTrue(GardenFactory())

    def test_set_managers(self):
        """ Test setting managers """
        managers = [ActiveUserFactory()]
        garden = GardenFactory(managers=managers)
        self.assertEqual(set(managers), set(garden.managers.all()))


class PlotFactoryTestCase(TestCase):
    def test_create(self):
        """ Test creation """
        self.assertTrue(PlotFactory())

    def test_set_crops(self):
        """ Test setting crops """
        crops = [CropFactory() for _ in range(5)]
        plot = PlotFactory(crops=crops)
        self.assertEqual(set(crops), set(plot.crops.all()))

    def test_zero_default(self):
        """ By default, no crops are generated """
        self.assertEqual(PlotFactory().crops.count(), 0)

    def test_no_crops(self):
        """ Make sure we can set no crops """
        plot = PlotFactory(crops=[])
        self.assertEqual(plot.crops.count(), 0)

    def test_crop_count(self):
        """ Passing crop_count generates the given number of crops """
        plot = PlotFactory(crop_count=5)
        self.assertEqual(plot.crops.count(), 5)

    def test_set_gardeners(self):
        """ Test setting gardeners """
        gardeners = [ActiveUserFactory()]
        plot = PlotFactory(gardeners=gardeners)
        self.assertEqual(set(gardeners), set(plot.gardeners.all()))


class PickFactoryTestCase(TestCase):
    def test_create(self):
        """ Test creation """
        self.assertTrue(PickFactory())


class OrderFactoryTestCase(TestCase):
    def test_create(self):
        """ Test creation """
        order = OrderFactory(
            start_date=Faker("past_date"), end_date=Faker("future_date")
        )
        self.assertTrue(order)


class ActiveUserFactoryTestCase(TestCase):
    def test_create(self):
        """ Test creation """
        self.assertTrue(ActiveUserFactory())

    def test_is_active(self):
        """ Ensure the user is active """
        self.assertTrue(ActiveUserFactory().is_active)


class GardenerFactoryTestCase(TestCase):
    def test_create(self):
        """ Test creation """
        self.assertTrue(GardenerFactory())

    def test_is_gardener(self):
        """ The generated user should be a gardener """
        self.assertTrue(GardenerFactory().is_gardener())

    def test_set_plots(self):
        """ Make sure we can set plots """
        plots = [PlotFactory() for _ in range(5)]
        gardener = GardenerFactory(plots=plots)
        for plot in plots:
            self.assertIn(gardener, plot.gardeners.all())

    def test_no_plots(self):
        """ Make sure we can set no plots """
        gardener = GardenerFactory(plots=[])
        self.assertTrue(gardener.plots.count(), 0)

    def test_gardener_only(self):
        """ By default, they're not a GM or Picker """
        self.assertFalse(GardenerFactory().is_garden_manager())
        self.assertFalse(GardenerFactory().is_picker())


class PickerFactoryTestCase(TestCase):
    def test_create(self):
        """ Test creation """
        self.assertTrue(PickerFactory())

    def test_is_picker(self):
        """ The generated user should be a picker """
        self.assertTrue(PickerFactory().is_picker())

    def test_picker_only(self):
        """ By default, they're not a gardener or GM """
        self.assertFalse(PickerFactory().is_gardener())
        self.assertFalse(PickerFactory().is_garden_manager())
