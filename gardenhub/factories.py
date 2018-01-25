from django.contrib.auth import get_user_model
import factory
from factory.django import DjangoModelFactory
from gardenhub.models import Garden, Plot, Crop, Order, Pick


class CropFactory(DjangoModelFactory):
    class Meta:
        model = Crop

    title = factory.Sequence(lambda n: "Crop #%s" % n)
    image = factory.django.ImageField()


class GardenFactory(DjangoModelFactory):
    class Meta:
        model = Garden

    title = factory.Sequence(lambda n: "Garden #%s" % n)
    address = factory.Sequence(lambda n: "%s GardenHub Avenue" % n)
    photo = factory.django.ImageField()

    @factory.post_generation
    def managers(self, create, extracted, **kwargs):
        if extracted:
            self.managers.set(extracted)


class PlotFactory(DjangoModelFactory):
    class Meta:
        model = Plot

    title = factory.Sequence(lambda n: str(n))
    garden = factory.SubFactory(GardenFactory)

    @factory.post_generation
    def crop_count(self, create, extracted, **kwargs):
        if extracted and not kwargs.get('crops'):
            self.crops.set([CropFactory() for _ in range(extracted)])

    @factory.post_generation
    def crops(self, create, extracted, **kwargs):
        if extracted:
            self.crops.set(extracted)

    @factory.post_generation
    def gardeners(self, create, extracted, **kwargs):
        if extracted:
            self.gardeners.set(extracted)


class ActiveUserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(
        lambda user: '{}.{}@gardenhub.dev'.format(
            user.first_name, user.last_name
        ).lower())
    photo = factory.django.ImageField()
    is_active = True


class GardenerFactory(ActiveUserFactory):
    @factory.post_generation
    def plots(self, create, extracted, **kwargs):
        if extracted:
            # Set plots if provided
            for plot in extracted:
                plot.gardeners.add(self)
        else:
            # Otherwise, add to a single plot
            PlotFactory().gardeners.add(self)


class PickerFactory(ActiveUserFactory):
    @factory.post_generation
    def picker_gardens(self, create, extracted, **kwargs):
        if extracted:
            # Set gardens if provided
            for garden in extracted:
                garden.pickers.add(self)
        else:
            # Otherwise, add to a single garden
            GardenFactory().pickers.add(self)


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    start_date = factory.Faker("date")
    end_date = factory.Faker("date")
    plot = factory.SubFactory(PlotFactory)
    requester = factory.SubFactory(ActiveUserFactory)


class PickFactory(DjangoModelFactory):
    class Meta:
        model = Pick

    picker = factory.SubFactory(PickerFactory)
    plot = factory.SubFactory(PlotFactory)
