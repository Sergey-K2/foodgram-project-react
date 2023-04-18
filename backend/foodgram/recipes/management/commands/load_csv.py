import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


def get_reader(file_name):
    csv_path = os.path.join(settings.BASE_DIR, "foodgram/data/", file_name)
    csv_file = open(csv_path, "r", encoding="utf-8")
    return csv.reader(csv_file, delimeter=",")


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_reader = get_reader("ingredients.csv")
        next(csv_reader, None)
        for row in csv_reader:
            obj, created = Ingredient.objects.get_or_create(
                name=row[0], unit=row[1]
            )
        print("Ингридиенты добавлены!")