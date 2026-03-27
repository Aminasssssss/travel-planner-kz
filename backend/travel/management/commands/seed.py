from django.core.management.base import BaseCommand
from travel.models import Destination, Category, Place

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Categories
        cats = {}
        for name in ['nature', 'history', 'food', 'active', 'photo']:
            c, _ = Category.objects.get_or_create(name=name)
            cats[name] = c

        # Almaty
        almaty, _ = Destination.objects.get_or_create(
            name='Almaty', region='almaty',
            defaults={'description': 'Largest city of Kazakhstan', 'season_best': 'all', 'image_url': ''}
        )
        Place.objects.get_or_create(name='Big Almaty Lake', defaults={
            'description': 'Beautiful mountain lake', 'price_level': 'budget',
            'latitude': 43.05, 'longitude': 76.98, 'rating': 4.8,
            'destination': almaty, 'category': cats['nature']
        })
        Place.objects.get_or_create(name='Shymbulak Ski Resort', defaults={
            'description': 'Top ski resort', 'price_level': 'luxury',
            'latitude': 43.14, 'longitude': 76.99, 'rating': 4.7,
            'destination': almaty, 'category': cats['active']
        })
        Place.objects.get_or_create(name='Green Bazaar', defaults={
            'description': 'Famous local market', 'price_level': 'budget',
            'latitude': 43.25, 'longitude': 76.94, 'rating': 4.3,
            'destination': almaty, 'category': cats['food']
        })
        Place.objects.get_or_create(name='Zenkov Cathedral', defaults={
            'description': 'Historic wooden cathedral', 'price_level': 'budget',
            'latitude': 43.26, 'longitude': 76.95, 'rating': 4.6,
            'destination': almaty, 'category': cats['history']
        })

        # Astana
        astana, _ = Destination.objects.get_or_create(
            name='Astana', region='astana',
            defaults={'description': 'Capital of Kazakhstan', 'season_best': 'summer', 'image_url': ''}
        )
        Place.objects.get_or_create(name='Baiterek Tower', defaults={
            'description': 'Symbol of Astana', 'price_level': 'mid',
            'latitude': 51.12, 'longitude': 71.43, 'rating': 4.5,
            'destination': astana, 'category': cats['photo']
        })
        Place.objects.get_or_create(name='Khan Shatyr', defaults={
            'description': 'Giant transparent tent', 'price_level': 'mid',
            'latitude': 51.13, 'longitude': 71.40, 'rating': 4.4,
            'destination': astana, 'category': cats['active']
        })
        Place.objects.get_or_create(name='National Museum', defaults={
            'description': 'History of Kazakhstan', 'price_level': 'budget',
            'latitude': 51.18, 'longitude': 71.44, 'rating': 4.3,
            'destination': astana, 'category': cats['history']
        })

        # Turkestan
        turkestan, _ = Destination.objects.get_or_create(
            name='Turkestan', region='turkestan',
            defaults={'description': 'Ancient city, spiritual capital', 'season_best': 'spring', 'image_url': ''}
        )
        Place.objects.get_or_create(name='Khoja Ahmed Yasawi Mausoleum', defaults={
            'description': 'UNESCO World Heritage Site', 'price_level': 'budget',
            'latitude': 43.29, 'longitude': 68.27, 'rating': 4.9,
            'destination': turkestan, 'category': cats['history']
        })

        self.stdout.write(self.style.SUCCESS('Seed data created successfully!'))