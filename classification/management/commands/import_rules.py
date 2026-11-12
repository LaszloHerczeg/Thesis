"""
Szófrekvencia CSV beolvasása és Rule objektumok létrehozása egy kategóriához.

Használat:
    python manage.py import_rules "<kategória neve (db-ben)>"
    python manage.py import_rules "<kategória neve>" --law-type <mappa_neve>
    python manage.py import_rules "<kategória neve>" --replace

A CSV helye:
    settings.DATA_DIR / "filtered csv" / <law_type> / "step2_filtered.csv"

A CSV első oszlopa a szó (-> Rule.expression), a második oszlop
a 100 000 szóra vetített előfordulás (-> Rule.weight).
"""

import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from case.models import Category
from classification.lookups import get_rules
from classification.models import Rule

FILTERED_CSV_DIR = Path(settings.DATA_DIR) / "filtered csv"
CSV_FILENAME = "step2_filtered.csv"


def parse_number(value):
    """Számmá alakítja a szöveget (tizedesvesszőt is elfogad); ha nem szám, None."""
    try:
        return float(value.strip().replace(",", "."))
    except (ValueError, AttributeError):
        return None


def detect_dialect(csv_path):
    """Megpróbálja kitalálni az elválasztó karaktert (vessző, pontosvessző, tab)."""
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        return csv.excel  # alapértelmezés: vesszővel elválasztott


def read_word_weights(csv_path):
    """
    Beolvassa a CSV-t, és visszaad egy {szó: gyakoriság} szótárt a fájlbeli sorrendben.

    - A fejlécsort (ahol a második oszlop nem szám) kihagyja.
    - Az üres vagy hiányos sorokat kihagyja.
    - Ha egy szó többször szerepel a fájlban, az első előfordulást tartja meg.
    """
    dialect = detect_dialect(csv_path)
    word_weights = {}

    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f, dialect):
            if len(row) < 2:
                continue
            word = row[0].strip()
            weight = parse_number(row[1])
            if not word or weight is None:
                continue  # fejléc vagy hibás sor
            word_weights.setdefault(word, weight)

    return word_weights


def list_law_type_folders():
    """A 'filtered csv' mappában található jogterület-mappák nevei, ábécérendben."""
    if not FILTERED_CSV_DIR.is_dir():
        return []
    return sorted(p.name for p in FILTERED_CSV_DIR.iterdir() if p.is_dir())


class Command(BaseCommand):
    help = (
        "Beolvassa a DATA_DIR/filtered csv/<law_type>/step2_filtered.csv fájlt, "
        "és minden szóhoz létrehoz egy Rule objektumot a megadott kategóriával, "
        "a gyakoriságot a weight mezőbe írva."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "category",
            help="A Category neve (Category.name), amelyhez a szabályok tartoznak.",
        )
        parser.add_argument(
            "--law-type",
            dest="law_type",
            default=None,
            help=(
                "A jogterület mappájának neve a 'filtered csv' mappán belül. "
                "Ha nincs megadva, a kategória nevével egyező mappát keresi."
            ),
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help=(
                "Az importálás előtt törli a megadott kategóriához tartozó összes "
                "meglévő Rule-t, majd elmenti az újakat."
            ),
        )

    def handle(self, *args, **options):
        category_name = options["category"]
        law_type = options["law_type"] or category_name

        # Mindkét argumentumot ellenőrizzük, mielőtt hibát jeleznénk,
        # hogy egyszerre lássuk az összes problémát.
        category, category_error = self.find_category(category_name)
        law_type_dir, law_type_error = self.find_law_type_dir(law_type)
        errors = [e for e in (category_error, law_type_error) if e]

        if errors:
            for error in errors:
                self.stderr.write(self.style.ERROR(error))
            self.print_available_options()
            raise CommandError("Érvénytelen argumentum.")

        csv_path = law_type_dir / CSV_FILENAME
        if not csv_path.is_file():
            raise CommandError(f"Nem található a CSV fájl: {csv_path}")

        word_weights = read_word_weights(csv_path)
        if not word_weights:
            self.stdout.write(self.style.WARNING(f"Nem található szó a fájlban: {csv_path}"))
            return

        # clear cache of rules
        get_rules.cache_clear()

        with transaction.atomic():
            deleted = self.delete_rules(category) if options["replace"] else 0
            created, updated, unchanged = self.save_rules(category, word_weights)

        summary = f"Kész ('{category}', {csv_path.parent.name}): "
        if options["replace"]:
            summary += f"{deleted} régi Rule törölve, "
        summary += (
            f"{created} új Rule létrehozva, {updated} meglévő súlya frissítve, "
            f"{unchanged} változatlan."
        )
        self.stdout.write(self.style.SUCCESS(summary))

    def find_category(self, name):
        """Visszaadja (kategória, None)-t, vagy hiba esetén (None, hibaüzenet)-et."""
        try:
            return Category.objects.get(name=name), None
        except Category.DoesNotExist:
            return None, f"Nem található kategória ezzel a névvel: '{name}'"
        except Category.MultipleObjectsReturned:
            return None, f"Több kategória is létezik ezzel a névvel: '{name}'"

    def find_law_type_dir(self, law_type):
        """Visszaadja (mappa, None)-t, vagy hiba esetén (None, hibaüzenet)-et."""
        folder = FILTERED_CSV_DIR / law_type
        if folder.is_dir():
            return folder, None
        return None, f"Nem található a jogterület mappája: {folder}"

    def print_available_options(self):
        """Kiírja az összes kategóriát (__str__ alapján) és a jogterület-mappákat."""
        self.stdout.write("\nElérhető kategóriák:")
        categories = Category.objects.all()
        if categories.exists():
            for category in categories:
                self.stdout.write(f"  - {category}")
        else:
            self.stdout.write("  (az adatbázisban nincs egyetlen kategória sem)")

        self.stdout.write(f"\nElérhető mappák ({FILTERED_CSV_DIR}):")
        folders = list_law_type_folders()
        if folders:
            for folder in folders:
                self.stdout.write(f"  - {folder}")
        else:
            self.stdout.write("  (nem található egyetlen mappa sem)")

    def delete_rules(self, category):
        """Törli a kategóriához tartozó összes Rule-t; visszaadja a törölt Rule-ok számát."""
        _, deleted_per_model = Rule.objects.filter(category=category).delete()
        return deleted_per_model.get(Rule._meta.label, 0)

    @transaction.atomic
    def save_rules(self, category, word_weights):
        """
        Elmenti a szavakat Rule objektumként, a gyakoriságot a weight mezőbe írva.
        Az is_positive és is_active mezőket nem állítja be, így azok a modell
        default értékét kapják.

        A kategóriánál már létező kifejezéseknél nem hoz létre új sort, hanem
        frissíti a súlyt, ha az eltér, így a parancs többször is futtatható.
        """
        existing = {
            rule.expression: rule
            for rule in Rule.objects.filter(
                category=category, expression__in=list(word_weights)
            )
        }

        new_rules = []
        changed_rules = []
        now = timezone.now()

        for word, weight in word_weights.items():
            rule = existing.get(word)
            if rule is None:
                new_rules.append(Rule(category=category, expression=word, weight=weight))
            elif rule.weight != weight:
                rule.weight = weight
                rule.updated_at = now  # bulk_update nem frissíti magától az auto_now mezőt
                changed_rules.append(rule)

        Rule.objects.bulk_create(new_rules, batch_size=1000)
        Rule.objects.bulk_update(changed_rules, ["weight", "updated_at"], batch_size=1000)

        unchanged = len(existing) - len(changed_rules)
        return len(new_rules), len(changed_rules), unchanged