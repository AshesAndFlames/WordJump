
import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from japanese.models import Flashcard


class Command(BaseCommand):

    help = "Import Japanese JLPT vocabulary from CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str
        )

    @transaction.atomic
    def handle(self, *args, **options):

        file_path = Path(options['csv_file'])

        if not file_path.is_file():
            raise CommandError(
                f"File not found: {file_path.resolve()}"
            )

        added = 0
        updated = 0
        skipped = 0

        valid_levels = {'N5', 'N4', 'N3'}

        required_columns = {
            'foreign_word',
            'translation',
            'part_of_speech',
            'example_sentence',
            'jlpt_level',
        }

        with file_path.open(
            'r',
            encoding='utf-8-sig',
            newline=''
        ) as file:

            reader = csv.DictReader(file)

            if not required_columns.issubset(
                reader.fieldnames or []
            ):
                raise CommandError(
                    'CSV is missing required columns.'
                )

            for row in reader:

                word = (
                    row.get('foreign_word') or ''
                ).strip()

                translation = (
                    row.get('translation') or ''
                ).strip()

                level = (
                    row.get('jlpt_level') or ''
                ).strip().upper()

                if not word or not translation:
                    skipped += 1
                    continue

                if level not in valid_levels:
                    raise CommandError(
                        f"Invalid JLPT level '{level}' "
                        f"for {word}"
                    )

                defaults = {
                    'translation': translation,
                    'part_of_speech': (
                        row.get('part_of_speech') or ''
                    ).strip(),
                    'example_sentence': (
                        row.get('example_sentence') or ''
                    ).strip(),
                }

                _, created = Flashcard.objects.update_or_create(
                    foreign_word=word,
                    jlpt_level=level,
                    defaults=defaults,
                )

                if created:
                    added += 1
                else:
                    updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                'Import complete!\n'
                f'Added: {added}\n'
                f'Updated: {updated}\n'
                f'Skipped: {skipped}'
            )
        )
