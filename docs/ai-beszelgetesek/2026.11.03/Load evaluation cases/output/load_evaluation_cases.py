"""
Load evaluation cases from a JSON file (located in settings.EVAL_DIR) into the
EvalCase model.

Expected JSON structure:

    {
        "<expected_category>": [
            {"key": "<key>", "description": "<description>"},
            ...
        ],
        ...
    }

Usage:
    python manage.py load_evaluation_cases
    python manage.py load_evaluation_cases --file other_cases.json
    python manage.py load_evaluation_cases --reset
"""

import json
from collections import Counter
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count

from evaluation.models import EvalCase

DEFAULT_FILENAME = "eval_cases.json"


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #

def get_json_path(filename):
    """Build the absolute path of the JSON file inside settings.EVAL_DIR."""
    eval_dir = getattr(settings, "EVAL_DIR", None)
    if not eval_dir:
        raise CommandError("EVAL_DIR is not defined in the settings file.")

    path = Path(eval_dir) / filename
    if not path.is_file():
        raise CommandError(f"JSON file not found: {path}")
    return path


def load_cases_from_json(path):
    """
    Read the JSON file and flatten it into a list of dicts:
        [{"key": ..., "description": ..., "expected_category": ...}, ...]

    Raises CommandError on invalid JSON, wrong structure or duplicate keys.
    """
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise CommandError(
            f"Invalid JSON in {path} (line {exc.lineno}, column {exc.colno}): {exc.msg}"
        ) from exc

    if not isinstance(data, dict):
        raise CommandError("The JSON root must be an object of {category: [cases]}.")

    cases = []
    for category, items in data.items():
        if not isinstance(items, list):
            raise CommandError(f'Category "{category}" must contain a list of cases.')

        for index, item in enumerate(items):
            if not isinstance(item, dict) or "key" not in item or "description" not in item:
                raise CommandError(
                    f'Case #{index + 1} in category "{category}" must have '
                    f'"key" and "description" fields.'
                )
            cases.append(
                {
                    "key": item["key"],
                    "description": item["description"],
                    "expected_category": category,
                }
            )

    duplicates = [key for key, n in Counter(c["key"] for c in cases).items() if n > 1]
    if duplicates:
        raise CommandError(f"Duplicate keys in the JSON file: {', '.join(duplicates)}")

    return cases


def find_existing_keys(cases):
    """Return the set of keys from `cases` that already exist in the database."""
    keys = [c["key"] for c in cases]
    return set(EvalCase.objects.filter(key__in=keys).values_list("key", flat=True))


def ask_yes_no(question):
    """Ask a yes/no question on the command line. Returns True for yes."""
    while True:
        try:
            answer = input(f"{question} [y/n]: ").strip().lower()
        except EOFError:
            return False
        if answer in ("y", "yes", "i", "igen"):
            return True
        if answer in ("n", "no", "nem"):
            return False
        print("Please answer 'y' or 'n'.")


def save_cases(cases, existing_keys):
    """
    Update the cases whose key already exists, create the rest.
    is_active is left to its model default for new cases.
    Returns (created_count, updated_count).
    """
    created = updated = 0
    new_objects = []

    for case in cases:
        if case["key"] in existing_keys:
            EvalCase.objects.filter(key=case["key"]).update(
                description=case["description"],
                expected_category=case["expected_category"],
            )
            updated += 1
        else:
            new_objects.append(
                EvalCase(
                    key=case["key"],
                    description=case["description"],
                    expected_category=case["expected_category"],
                )
            )

    EvalCase.objects.bulk_create(new_objects)
    created = len(new_objects)
    return created, updated


def print_summary(stdout, style):
    """Print the total number of cases and the number of cases per category."""
    total = EvalCase.objects.count()
    per_category = (
        EvalCase.objects.values("expected_category")
        .annotate(count=Count("id"))
        .order_by("expected_category")
    )

    stdout.write(style.MIGRATE_HEADING(f"\nTotal number of cases: {total}"))
    stdout.write("Cases per category:")
    for row in per_category:
        stdout.write(f"  {row['expected_category']}: {row['count']}")


# --------------------------------------------------------------------------- #
# Command
# --------------------------------------------------------------------------- #

class Command(BaseCommand):
    help = "Load evaluation cases from a JSON file in EVAL_DIR into the EvalCase model."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete ALL existing EvalCase objects before loading the new batch.",
        )
        parser.add_argument(
            "--file",
            default=DEFAULT_FILENAME,
            help=f"Name of the JSON file inside EVAL_DIR (default: {DEFAULT_FILENAME}).",
        )

    def handle(self, *args, **options):
        path = get_json_path(options["file"])
        cases = load_cases_from_json(path)
        self.stdout.write(f"Read {len(cases)} cases from {path}")

        if options["reset"]:
            with transaction.atomic():
                deleted, _ = EvalCase.objects.all().delete()
                created, updated = save_cases(cases, existing_keys=set())
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing cases."))
        else:
            existing_keys = find_existing_keys(cases)

            if existing_keys:
                self.stdout.write(
                    self.style.WARNING(
                        f"{len(existing_keys)} case(s) with the same key already exist:"
                    )
                )
                for key in sorted(existing_keys):
                    self.stdout.write(f"  - {key}")

                if not ask_yes_no("Do you want to override these cases?"):
                    self.stdout.write(self.style.ERROR("Aborted. Nothing was saved."))
                    return

            with transaction.atomic():
                created, updated = save_cases(cases, existing_keys)

        self.stdout.write(
            self.style.SUCCESS(f"Created {created} case(s), overridden {updated} case(s).")
        )
        print_summary(self.stdout, self.style)
