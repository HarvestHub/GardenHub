import os
from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from gardenhub.models import Crop
from ._crops_list import crops_list


class Command(BaseCommand):
    help = 'Populates 100+ sane default crops into the database'

    def handle(self, *args, **options):
        # Directory where the crop images exist
        CROPS_DIR = os.path.join(settings.BASE_DIR, 'crops')

        # Loop through list of crops and create them
        # The list is in _crops_list.py
        for crop_title in crops_list:
            # This *should* be the crop's filename
            filename = '{}.jpg'.format(crop_title.replace(' ', '_'))
            # File representing the exact location of the image
            crop_image = File(open(
                os.path.join(CROPS_DIR, filename), 'rb'))
            try:
                # Create the crop and copy the image into it
                crop = Crop.objects.create(title=crop_title)
                crop.image.save(filename, crop_image)

                self.stdout.write(self.style.SUCCESS(
                    'Created {}.'.format(crop_title)
                ))
            except IntegrityError:
                # If the crop already exists, it'll raise an IntegrityError
                # so just notify that it was skipped
                self.stdout.write(self.style.WARNING(
                    '{} already exists. Skipping.'.format(crop_title)
                ))

        self.stdout.write(self.style.SUCCESS('Finished creating crops!'))
