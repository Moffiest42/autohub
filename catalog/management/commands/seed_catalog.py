from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from catalog.models import Category, Mechanic, Service

CATEGORIES = [
    'Диагностика',
    'Техническое обслуживание',
    'Ремонт',
    'Шиномонтаж',
]

MECHANICS = [
    ('Андрей Соколов', 'Двигатели и подвеска', 8),
    ('Игорь Лебедев', 'ТО и климат', 5),
    ('Сергей Волков', 'Тормоза и ГРМ', 10),
    ('Дмитрий Орлов', 'Шиномонтаж и балансировка', 6),
    ('Максим Крылов', 'Электрика и диагностика', 7),
]

SERVICES = [
    ('Компьютерная диагностика', 'Диагностика', 'Максим Крылов', '1800', 45,
     'Считывание ошибок всеми блоками управления, проверка датчиков и проводки. '
     'По итогам — список неисправностей с ценами до начала ремонта.'),
    ('Диагностика двигателя', 'Диагностика', 'Андрей Соколов', '1500', 60,
     'Проверка компрессии, состояния свечей, ремней и течей. '
     'Заключение о состоянии двигателя с рекомендациями.'),
    ('Замена масла и фильтров', 'Техническое обслуживание', 'Игорь Лебедев', '900', 40,
     'Замена моторного масла, масляного и воздушного фильтров. '
     'Проверка уровня остальных жидкостей бесплатно.'),
    ('Заправка кондиционера', 'Техническое обслуживание', 'Игорь Лебедев', '2500', 60,
     'Вакуумирование системы, проверка на утечки, заправка хладагентом '
     'и антибактериальная обработка испарителя.'),
    ('Ремонт тормозной системы', 'Ремонт', 'Сергей Волков', '3000', 90,
     'Замена колодок и дисков, прокачка тормозной системы, '
     'проверка суппортов и шлангов. Гарантия на работы 1 год.'),
    ('Ремонт подвески', 'Ремонт', 'Андрей Соколов', '4500', 120,
     'Замена рычагов, сайлентблоков, стоек и подшипников. '
     'После ремонта — контрольный заезд и проверка развала-схождения.'),
    ('Замена ремня ГРМ', 'Ремонт', 'Сергей Волков', '6000', 180,
     'Замена ремня, роликов натяжителя и обводного ролика. '
     'При необходимости — замена помпы. Отметка о пробеге в заказ-наряде.'),
    ('Шиномонтаж и балансировка', 'Шиномонтаж', 'Дмитрий Орлов', '2200', 50,
     'Снятие, монтаж и балансировка четырёх колёс на стенде. '
     'Проверка давления и состояния протектора.'),
]

DEMO_USERS = [
    ('admin_demo', 'AdminPass2026', 'Администратор СТО', 'admin@autofix.ru', '+74951234567', 'ADMIN'),
    ('user_demo', 'UserPass2026', 'Иванов Иван Иванович', 'user@autofix.ru', '+79001234567', 'USER'),
]


class Command(BaseCommand):
    help = 'Наполняет каталог автосервиса: категории, механики, услуги (идемпотентно)'

    def add_arguments(self, parser):
        parser.add_argument('--with-users', action='store_true',
                            help='Дополнительно создать демо-пользователей USER и ADMIN')

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for name in CATEGORIES:
            obj, created = Category.objects.get_or_create(name=name)
            categories[name] = obj
            if created:
                self.stdout.write(f'  + категория: {name}')

        mechanics = {}
        for full_name, specialization, experience in MECHANICS:
            obj, created = Mechanic.objects.get_or_create(
                full_name=full_name,
                defaults={'specialization': specialization, 'experience': experience},
            )
            mechanics[full_name] = obj
            if created:
                self.stdout.write(f'  + механик: {full_name}')

        created_count = 0
        for title, category, mechanic, price, duration, description in SERVICES:
            _, created = Service.objects.get_or_create(
                title=title,
                defaults={
                    'category': categories[category],
                    'mechanic': mechanics[mechanic],
                    'price': Decimal(price),
                    'duration_minutes': duration,
                    'description': description,
                },
            )
            created_count += int(created)
            if created:
                self.stdout.write(f'  + услуга: {title}')

        if options['with_users']:
            for username, password, full_name, email, phone, role in DEMO_USERS:
                if User.objects.filter(username=username).exists():
                    self.stdout.write(f'  = пользователь {username} уже есть')
                    continue
                User.objects.create_user(
                    username=username, password=password, full_name=full_name,
                    email=email, phone=phone, role=role,
                )
                self.stdout.write(f'  + пользователь: {username} ({role})')

        self.stdout.write(self.style.SUCCESS(
            f'Готово. Новых услуг: {created_count}. '
            f'Всего — категорий: {Category.objects.count()}, '
            f'механиков: {Mechanic.objects.count()}, услуг: {Service.objects.count()}.'
        ))