from django.core.management.base import BaseCommand
from travel.models import Event, Destination
from datetime import date, time, timedelta

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Event.objects.all().delete()
        
        almaty = Destination.objects.get(name='Алматы')
        astana = Destination.objects.get(name='Астана')
        
        today = date.today()
        
        events = [
            {'city': almaty, 'title': 'Вечер джаза', 'category': 'concert', 'location': 'Дворец Республики', 'description': 'Лучшие джазовые музыканты города в одном концерте. Прозвучат классические и современные композиции.', 'date': today + timedelta(days=2), 'time': time(19, 0), 'price_from': 5000, 'is_sponsored': True, 'sponsor_label': 'Генеральный партнёр'},
            {'city': almaty, 'title': 'Гастро-ужин от шефа', 'category': 'food', 'location': 'Ресторан "Афиша"', 'description': 'Эксклюзивный ужин из 5 блюд от шеф-повара ресторана. В меню авторские позиции и винное сопровождение.', 'date': today + timedelta(days=1), 'time': time(18, 30), 'price_from': 15000, 'is_sponsored': True, 'sponsor_label': 'Партнёр'},
            
            {'city': almaty, 'title': 'Мастер-класс по акварели', 'category': 'masterclass', 'location': 'Арт-студия "Палитра"', 'description': 'Научитесь основам акварельной живописи за 3 часа. Все материалы включены в стоимость.', 'date': today + timedelta(days=3), 'time': time(15, 0), 'price_from': 3000, 'is_sponsored': False, 'sponsor_label': ''},
            {'city': almaty, 'title': 'Спектакль "Ревизор"', 'category': 'theatre', 'location': 'Театр им. Ауэзова', 'description': 'Классическая комедия Гоголя в современной постановке. Блистательная игра актёров.', 'date': today + timedelta(days=4), 'time': time(18, 0), 'price_from': 2000, 'is_sponsored': False, 'sponsor_label': ''},
            {'city': almaty, 'title': 'Выставка современного искусства', 'category': 'exhibition', 'location': 'Галерея ART', 'description': 'Работы молодых казахстанских художников. Живопись, скульптура, инсталляции.', 'date': today + timedelta(days=5), 'time': time(11, 0), 'price_from': 1000, 'is_sponsored': False, 'sponsor_label': ''},
            {'city': almaty, 'title': 'Йога в парке', 'category': 'sport', 'location': 'Парк Первого Президента', 'description': 'Бесплатное занятие йогой на свежем воздухе. Подходит для любого уровня подготовки.', 'date': today + timedelta(days=1), 'time': time(9, 0), 'price_from': 0, 'is_sponsored': False, 'sponsor_label': ''},
            
            {'city': astana, 'title': 'Концерт симфонического оркестра', 'category': 'concert', 'location': 'Астана Опера', 'description': 'Произведения Чайковского и Рахманинова в исполнении симфонического оркестра.', 'date': today + timedelta(days=2), 'time': time(19, 0), 'price_from': 8000, 'is_sponsored': True, 'sponsor_label': 'Партнёр'},
            
            {'city': astana, 'title': 'Фестиваль уличной еды', 'category': 'food', 'location': 'Парк "Астана"', 'description': 'Лучшие стритфуд-проекты города. Бургеры, пицца, азиатская кухня и десерты.', 'date': today + timedelta(days=1), 'time': time(12, 0), 'price_from': 0, 'is_sponsored': False, 'sponsor_label': ''},
            {'city': astana, 'title': 'Детский спектакль', 'category': 'kids', 'location': 'Кукольный театр', 'description': 'Сказка "Три поросёнка" для самых маленьких зрителей. Яркие куклы и весёлая музыка.', 'date': today + timedelta(days=3), 'time': time(11, 0), 'price_from': 1500, 'is_sponsored': False, 'sponsor_label': ''},
        ]
        
        for e in events:
            Event.objects.create(**e)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Создано {len(events)} событий'))