from django.db import models
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField
from gardenhub.utils import localdate

from .managers import OrderQuerySet, UserManager


class Crop(models.Model):
    """
    A crop represents an item that may be picked, such as a zuchini or an
    orange. Crops are stored in a master list, managed by the site admin, and
    may be listed on Orders or Picks.
    """
    title = models.CharField(
        max_length=255, unique=True,
        help_text="All lowercase name of this crop.")
    image = models.ImageField(
        help_text="Photo of this crop.", upload_to="crops")

    def __str__(self):
        return self.title


class Affiliation(models.Model):
    """
    A group of affiliated gardens.
    """
    title = models.CharField(
        max_length=255,
        help_text="The name of this affiliation."
    )
    managers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True,
        help_text="People who can edit this affiliation."
    )

    def __str__(self):
        return self.title


class Garden(models.Model):
    """
    A whole landscape, divided into many plots. Managed by Garden Managers.
    """
    title = models.CharField(max_length=255)

    managers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='gardens', blank=True,
        help_text="People who can edit this garden, edit plots on this garden,"
                  " and view/place orders for plots on this garden."
    )

    address = models.CharField(
        max_length=255,
        help_text="The full, neatly-formatted mailing address of this garden."
    )

    affiliations = models.ManyToManyField(
        Affiliation, related_name='gardens', blank=True,
        help_text="This garden's affiliations."
    )

    photo = models.ImageField(
        blank=True, help_text="A photo of this garden.", upload_to="gardens"
    )

    map_image = models.ImageField(
        blank=True, help_text="A map of this garden.", upload_to="maps"
    )

    pickers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='+', blank=True,
        help_text="People who are assigned to fulfill orders on this garden."
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('garden-detail', args=[self.id])


class Plot(models.Model):
    """
    Subdivision of a Garden, allocated to a Gardener for growing food.
    """
    title = models.CharField(
        max_length=255,
        help_text=_("The plot's name is probably a number, like 11. "
                    "The plot should be clearly labeled with a sign."
                    ))

    garden = models.ForeignKey(
        'Garden', on_delete=models.CASCADE, related_name='plots',
        help_text="The garden this plot is a part of."
    )

    gardeners = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='plots', blank=True,
        help_text="People who grow food on this plot. Listing them here "
                  "enables them to place orders."
    )

    crops = models.ManyToManyField('Crop', related_name='+', blank=True)

    def __str__(self):
        return "{} [{}]".format(self.garden.title, self.title)


class Order(models.Model):
    """
    A request from a Gardener or Garden Manager to enlist a particular Plot for
    picking over a specified number of days.
    """
    timestamp = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text="The exact moment this order was submitted."
    )
    plot = models.ForeignKey(
        'Plot', on_delete=models.PROTECT,
        help_text="The plot this order targets for picking."
    )
    pick_all = models.BooleanField(
        default=False,
        help_text="Whether all crops on the physical plot should be picked "
                  "or not. When checked, the `crops` field is ignored."
    )
    crops = models.ManyToManyField(
        'Crop', blank=True,
        help_text="Crops that should be picked for this order."
    )
    start_date = models.DateField(
        help_text="The day picking should begin for this order."
    )
    end_date = models.DateField(
        help_text="The day picking should end for this order."
    )
    canceled = models.BooleanField(
        default=False,
        help_text="Whether or not this order has been canceled."
    )
    canceled_timestamp = models.DateTimeField(
        null=True, blank=True,
        help_text="The moment this order was canceled, if so."
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        help_text="Person who submitted this order."
    )
    comment = models.TextField(
        blank=True,
        help_text="Additional comments about this order."
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('order-detail', args=[self.id])

    def progress(self):
        """ Percentage this order is complete, as a decimal between 0-100. """
        # Total amount of time this order covers
        start_time = localdate(self.start_date)
        end_time = localdate(self.end_date)
        duration = (end_time - start_time).total_seconds()

        # Amount of time already passed through this order's range
        now = timezone.now()
        elapsed = (now - start_time).total_seconds()

        # Calculate the completeness
        percentage = (elapsed / duration) * 100

        # Force bounds
        return min(100, max(0, percentage))

    def is_open(self):
        """ Whether this Order is open. """
        return self in Order.objects.open()

    def is_closed(self):
        """ Whether this Order is closed. """
        return self in Order.objects.closed()

    def is_active(self):
        """ Whether this Order is active. """
        return self in Order.objects.active()

    def was_picked_today(self):
        """
        True if at least one Pick was submitted today for the Order's Plot.
        """
        return self in Order.objects.picked_today()

    def get_picks(self):
        """
        Return the list of Picks that occurred on this Order's plot within
        this Order's timeframe.
        """
        return Pick.objects.filter(
            Q(plot__id=self.plot.id) &
            Q(timestamp__gte=localdate(self.start_date)) &
            Q(timestamp__lte=localdate(self.end_date))
        )

    def get_status_icon(self):
        """
        Returns a Semantic UI status icon class string depending on this
        order's status. This may be removed in the future.
        """
        if self.canceled:
            return "red ban"
        elif self.is_active():
            return "green circle"
        elif self.is_closed():
            return "grey check circle"
        else:
            return "grey circle"


class Pick(models.Model):
    """
    A submission by a picker signifying that certain Crops have been picked
    from a particular Plot at a particular time.
    """
    timestamp = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text="The exact moment this pick was submitted."
    )
    picker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        help_text="Person who submitted this pick."
    )
    plot = models.ForeignKey(
        Plot, on_delete=models.PROTECT, related_name='picks',
        help_text="Plot this pick occurred upon."
    )
    crops = models.ManyToManyField(
        Crop,
        help_text="Crops that were harvested by this pick."
    )
    comment = models.TextField(
        blank=True,
        help_text="Additional comments about this pick."
    )

    def __str__(self):
        return str(self.id)

    def inquirers(self):
        """ People to notify about this pick. """
        gardeners = self.plot.gardeners.all()
        requesters = [
            order.requester
            for order
            in Order.objects.active().filter(plot__id=self.plot.id)
        ]
        # Coerce to set to get distinct values
        return list(set(list(gardeners) + requesters))


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user class for GardenHub users. This is necessary because we want to
    authorize users by their email address (and provide a few extra fields).
    """
    email = models.EmailField(
        _('email address'), unique=True,
        help_text="The user's email address, which is used for notifications "
                  "and doubles as the username for logging in."
    )
    phone_number = PhoneNumberField(
        blank=True,
        help_text="The user's phone number, so site admins can directly "
                  "contact them if needed."
    )
    first_name = models.CharField(
        _('first name'), max_length=30,
        help_text="The user's given name or nickname, sometimes used in a "
                  "casual context."
    )
    last_name = models.CharField(
        _('last name'), max_length=150,
        help_text="The user's family name, sometimes used to distinguish one "
                  "user from another."
    )
    photo = models.ImageField(
        _('photo'), blank=True, upload_to="users",
        help_text="A photo of the user or an avatar."
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'
        ),
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,  # Users may be created and assigned to Gardens/Plots
                        # before they activate their account
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(
        _('date joined'), default=timezone.now,
        help_text="The exact moment this user joined the website."
    )

    activation_token = models.CharField(
        max_length=36, unique=True, blank=True, null=True,
        help_text="A temporary token used to activate the user's account "
                  "upon being invited to the site initially."
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.get_full_name()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_gardens(self):
        """
        Return all the Gardens the given user can edit.
        """
        return Garden.objects.filter(managers__id=self.id)

    def get_plots(self):
        """
        Return all the Plots the given user can edit. Users can edit any plot
        which they are a gardener on, and any plot in a garden they manage.
        """
        return Plot.objects.filter(
            Q(gardeners__id=self.id) | Q(garden__managers__id=self.id)
        ).distinct()

    def get_orders(self):
        """
        Return all Orders for the given user's Plots and Gardens.
        """
        plot_ids = [plot.id for plot in self.get_plots().all()]
        return Order.objects.filter(plot__id__in=plot_ids)

    def get_picker_gardens(self):
        """
        Return all Gardens where the user is in Garden.picker.
        """
        return Garden.objects.filter(pickers__id=self.id)

    def get_picker_orders(self):
        """
        Return all Orders this user is assigned to fulfill.
        """
        return Order.objects.filter(plot__garden__pickers__id=self.id)

    def get_peers(self):
        """
        Return all the Users within every Plot and Garden that you manage,
        except yourself.
        """
        return get_user_model().objects.filter(
            Q(gardens__id__in=[garden.id for garden in self.get_gardens()]) |
            Q(plots__id__in=[plot.id for plot in self.get_plots()])
        ).distinct().exclude(id=self.id)

    def is_garden_manager(self):
        """
        A garden manager is someone who facilitates renting Plots of a Garden
        out to Gardeners. Any person who is set as Garden.manager on at least
        one Garden.
        """
        return self.get_gardens().count() > 0

    def is_gardener(self):
        """
        A gardener is someone who rents a garden Plot and grows food there.
        Gardeners are assigned to Plot.gardener on at least one Plot. GM's of
        a garden with plots are also considered gardeners.
        """
        return self.get_plots().count() > 0

    # FIXME: Reassess the need for this.
    def is_anything(self):
        """
        GardenHub is only useful if the logged-in user can manage any garden or
        plot. If not, that is very sad. :(
        """
        return self.is_gardener() or self.is_garden_manager()

    def is_picker(self):
        """
        A picker is someone who is assigned to fulfill Orders on a Garden. They
        will submit Picks over the duration of the Orders.
        """
        return Garden.objects.filter(pickers__id=self.id).count() > 0

    def has_orders(self):
        """
        Determine whether the user has any orders at all.
        """
        return self.get_orders().count() > 0

    def can_edit_garden(self, garden):
        """
        Can the given user manage this garden?
        True if the user is listed in Garden.managers for that garden.
        False otherwise.
        """
        return self in garden.managers.all()

    def can_edit_plot(self, plot):
        """
        Can the given user manage this plot?
        True if the user is listed in Plot.gardeners for that plot, OR the user
        is listed in Garden.managers for the garden in Plot.garden.
        False otherwise.
        """
        return self in plot.gardeners.all() \
            or self in plot.garden.managers.all()

    def can_edit_order(self, order):
        """
        Can the given user manage this order?
        True if the user can edit Order.plot for that order.
        False otherwise.
        """
        return self.can_edit_plot(order.plot)

    def is_order_picker(self, order):
        """
        Is the user assigned as a picker on this order?
        True if the user is listed in Order.plot.garden.pickers.
        False otherwise.
        """
        return self in order.plot.garden.pickers.all()
