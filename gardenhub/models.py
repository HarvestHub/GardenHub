import uuid
from django.db import models
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _


class Crop(models.Model):
    """
    A crop represents an item that may be harvested, such as a zuchini or an
    orange. Crops are stored in a master list, managed by the site admin, and
    may be listed on Orders or Harvests.
    """
    title = models.CharField(max_length=255)
    image = models.ImageField()

    def __str__(self):
        return self.title


class Affiliation(models.Model):
    """
    A group of affiliated gardens.
    """
    title = models.CharField(max_length=255)
    managers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.title


class Garden(models.Model):
    """
    A whole landscape, divided into many plots. Managed by Garden Managers.
    """
    title = models.CharField(max_length=255)
    managers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='gardens', blank=True)
    address = models.CharField(max_length=255)
    affiliations = models.ManyToManyField(Affiliation, related_name='gardens', blank=True)
    photo = models.ImageField(blank=True)

    def __str__(self):
        return self.title


class Plot(models.Model):
    """
    Subdivision of a Garden, allocated to a Gardener for growing food.
    """
    title = models.CharField(
        max_length=255,
        help_text=_(
            "The plot's name is probably a number, like 11. "
            "The plot should be clearly labeled with a sign."
        ))
    garden = models.ForeignKey('Garden', models.CASCADE, related_name='plots')
    gardeners = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='plots', blank=True)
    crops = models.ManyToManyField('Crop', related_name='+', blank=True)

    def __str__(self):
        return "{} [{}]".format(self.garden.title, self.title)


class Order(models.Model):
    """
    A request from a Gardener or Garden Manager to enlist a particular Plot for
    Harvest over a specified number of days.
    """
    plot = models.ForeignKey('Plot', models.DO_NOTHING)
    crops = models.ManyToManyField('Crop')
    start_date = models.DateField()
    end_date = models.DateField()
    canceled = models.BooleanField(default=False)
    canceled_date = models.DateField(null=True, blank=True)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING)

    def __str__(self):
        return str(self.id)


class Harvest(models.Model):
    """
    A submission by an Employee signifying that Crops have been picked from a
    particular Plot on a particular day.
    """
    harvest_date = models.DateField()
    status = models.CharField(
        max_length=255,
        choices=(
            ('incomplete', 'Incomplete'),
            ('finished', 'Finished'),
        ),
    )
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING)

    def __str__(self):
        return str(self.id)


class UserManager(BaseUserManager):
    """
    Custom User manager because the custom User model only does auth by email.
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def get_or_invite_users(self, emails, request):
        """
        Gets or creates users from the list of emails. When a user is created
        they are sent an invitation email.
        """
        users = []

        # Loop through the list of emails
        for email in emails:
            # Get or create a user from the email
            user, created = get_user_model().objects.get_or_create(email=email)
            # If the user was just newly created...
            if created:
                # Generate a random token this user can activate their account with
                user.activation_token = str(uuid.uuid4())
                user.save()
                # Send the user an invitation email with their activation token
                inviter = request.user
                activate_url = request.build_absolute_uri('/activate/{}/'.format(user.activation_token))
                user.email_user(
                    subject="{} invited you to join GardenHub".format(inviter.get_full_name()),
                    message=render_to_string(
                        'gardenhub/email/invitation.txt', {
                            'inviter': inviter,
                            'activate_url': activate_url
                        }
                    )
                )

            users.append(user)

        return users


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user class for GardenHub users. This is necessary because we want to
    authorize users by their email address (and provide a few extra fields).
    """
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    photo = models.ImageField(_('photo'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=False, # Users may be created and assigned to Gardens/Plots before they activate their account
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    activation_token = models.CharField(
        max_length=36, unique=True, blank=True, null=True
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

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
        plot_ids = [ plot.id for plot in self.get_plots().all() ]
        return Order.objects.filter(plot__id__in=plot_ids)

    def get_peers(self):
        """
        Return all the Users within every Plot and Garden that you manage,
        except yourself.
        """
        return get_user_model().objects.filter(
            Q(gardens__id__in=[ garden.id for garden in self.get_gardens() ]) |
            Q(plots__id__in=[ plot.id for plot in self.get_plots() ])
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
        Gardeners are assigned to Plot.gardener on at least one Plot.
        """
        return self.get_plots().count() > 0

    def is_anything(self):
        """
        GardenHub is only useful if the logged-in user can manage any garden or
        plot. If not, that is very sad. :(
        """
        return self.is_gardener() or self.is_garden_manager()

    def has_open_orders(self):
        """
        Determine whether or not a user has any current open harvests for home
        display.
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
        return self in plot.gardeners.all() or self in plot.garden.managers.all()

    def can_edit_order(self, order):
        """
        Can the given user manage this order?
        True if the user can edit Order.plot for that order.
        False otherwise.
        """
        return self.can_edit_plot(order.plot)
