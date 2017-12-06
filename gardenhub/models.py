from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils import timezone
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
    managers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='+')

    def __str__(self):
        return self.title

class Garden(models.Model):
    """
    A whole landscape, divided into many plots. Managed by Garden Managers.
    """
    title = models.CharField(max_length=255)
    managers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='+')
    address = models.CharField(max_length=255)
    affiliations = models.ManyToManyField(Affiliation, related_name='+')

    def __str__(self):
        return self.title


class Plot(models.Model):
    """
    Subdivision of a Garden, allocated to a Gardener for growing food.
    """
    title = models.CharField(max_length=255)
    garden = models.ForeignKey('Garden', models.CASCADE)
    gardeners = models.ManyToManyField(settings.AUTH_USER_MODEL)
    crops = models.ManyToManyField('Crop')

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
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user class for GardenHub users. This is necessary because we want to
    authorize users by their email address (and provide a few extra fields).
    """
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

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


"""
There are several conceptual types of users that we should be aware of.

1. Site Administrator -- Has full access to all data, and is granted the ability
   to invite any new member to the site. TBD: Identifying them programatically.

2. Garden Manager -- Someone who facilitates renting Plots of a Garden out to
   Gardeners. Any person who is set as Garden.manager on at least one Garden.

3. Gardener -- Someone who rents a garden Plot and grows food there. Gardeners
   are assigned to Plot.gardener on at least one Plot.

4. Employee -- A hired employee responsible for fulfilling Orders. It is safe to
   say that anyone with an Order assigned to them is an Employee, but TBD:
   figure out how to determine them programatically when there's no active
   order.
"""
