from datetime import date
import uuid
from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager
from django.template.loader import render_to_string


class OrderQuerySet(models.QuerySet):
    """
    Custom QuerySet for advanced filtering of orders.
    """
    def completed(self):
        """ Orders that have finished. """
        return self.filter(end_date__lt=date.today())

    def open(self):
        """ Orders that have not finished but also may not have begun. """
        return self.filter(end_date__gt=date.today())

    def upcoming(self):
        """ Orders that have not yet begun. """
        return self.filter(start_date__gt=date.today())

    def active(self):
        """ All active orders. """
        return self.filter(
            Q(end_date__gte=date.today()) &
            Q(start_date__lte=date.today())
        )

    def inactive(self):
        """ All inactive orders. """
        return self.filter(
            Q(end_date__lt=date.today()) |
            Q(start_date__gt=date.today())
        )

    def picked_today(self):
        """ Orders that have at least one Pick from today. """
        return self.filter(plot__picks__timestamp__gte=date.today())

    def unpicked_today(self):
        """ Orders that have no Picks from today. """
        return self.exclude(plot__picks__timestamp__gte=date.today())


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
                # Generate a random token for account activation
                user.activation_token = str(uuid.uuid4())
                user.save()
                # Send the user an invitation email with their activation token
                inviter = request.user
                activate_url = request.build_absolute_uri(
                    '/activate/{}/'.format(user.activation_token)
                )
                user.email_user(
                    subject="{} invited you to join GardenHub".format(
                        inviter.get_full_name()),
                    message=render_to_string(
                        'gardenhub/email_invitation.txt', {
                            'inviter': inviter,
                            'activate_url': activate_url
                        }
                    )
                )

            users.append(user)

        return users
