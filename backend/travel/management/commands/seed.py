from django.core.management.base import BaseCommand
from travel.models import Destination, Category, Place
import pandas as pd
import os

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Place.objects.all().delete()
        Category.objects.all().delete()
        Destination.objects.all().delete()

        categories = {}
        for cat in ['active', 'nature', 'history', 'food', 'photo', 'culture', 'nightlife', 'shopping', 'family', 'lifestyle']:
            c, _ = Category.objects.get_or_create(name=cat)
            categories[cat] = c

        excel_path = os.path.join(os.path.dirname(__file__), 'kazakhstan_tourism_FINAL_v7.xlsx')
        df = pd.read_excel(excel_path, sheet_name='Места (Places)')

        budget_map = {0: 'budget', 1: 'budget', 2: 'mid', 3: 'luxury'}
        destinations = {}

        for _, row in df.iterrows():
            city = str(row['Город'])
            region = str(row['Регион'])
            if city not in destinations:
                d, _ = Destination.objects.get_or_create(
                    name=city,
                    defaults={
                        'region': region,
                        'description': f'{city} — beautiful city in Kazakhstan',
                        'season_best': 'all',
                        'image_url': ''
                    }
                )
                destinations[city] = d

        count = 0
        for _, row in df.iterrows():
            city = str(row['Город'])
            category = str(row['Категория'])
            price_num = int(row['Цена (уровень 0–3)']) if pd.notna(row['Цена (уровень 0–3)']) else 1
            price_level = budget_map.get(price_num, 'budget')

            Place.objects.get_or_create(
                name=str(row['Название']),
                destination=destinations[city],
                defaults={
                    'description': str(row['Описание EN'])[:500] if pd.notna(row['Описание EN']) else '',
                    'price_level': price_level,
                    'price_tenge': int(row['Цена (тенге)']) if pd.notna(row['Цена (тенге)']) else 0,
                    'open_hours': str(row['Часы работы'])[:100] if pd.notna(row['Часы работы']) else '',
                    'best_season': str(row['Лучший сезон'])[:100] if pd.notna(row['Лучший сезон']) else 'all',
                    'duration_hours': float(row['Продолж. (часы)']) if pd.notna(row['Продолж. (часы)']) else 2.0,
                    'latitude': float(row['Широта']) if pd.notna(row['Широта']) else 0,
                    'longitude': float(row['Долгота']) if pd.notna(row['Долгота']) else 0,
                    'rating': float(row['Рейтинг']) if pd.notna(row['Рейтинг']) else 4.0,
                    'tags': str(row['Теги'])[:300] if pd.notna(row['Теги']) else '',
                    'is_indoor': bool(int(row['Внутри (0/1)'])) if pd.notna(row['Внутри (0/1)']) else False,
                    'category': categories.get(category, categories['nature']),
                }
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Seeded {count} places across {len(destinations)} cities!'))